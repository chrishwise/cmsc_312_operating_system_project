import random
import threading

from process import Process
from operation import Operation
from xml.etree import ElementTree
from threading import *
import time


class CpuCore:
    time_slice = 30

    def __init__(self):
        self.processes = []
        self.new_queue = []
        self.ready_queue = []
        self.waiting_queue = []
        self.exit_queue = []
        self.pid_counter = 0
        self.memory_available = 1024
        self.memory_lock = Lock()
        self.memory_condition = Condition(self.memory_lock)
        self.critical_lock = Lock()
        self.semaphore = Semaphore(4)

    def generate_from_file(self, file_name):
        """Parses the given file and adds all of it's operations to a new process and adds it to processes list"""
        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        operations = root.findall('operation')
        memory = int(root.find('memory').text)
        critical = False
        new_process = Process(self.pid_counter, memory)
        for o in operations:
            name = o.text.strip()
            has_critical = o.find('critical')
            if has_critical is None:    # Bug fix. Python elements return None when they are found without sub-elements
                critical = True
            min_time = int(o.find('min').text)
            max_time = int(o.find('max').text)
            new_operation = Operation(name, min_time, max_time, critical)
            new_process.add_operation(new_operation)
        self.processes.append(new_process)
        self.new_queue.append(new_process)
        self.pid_counter += 1
        return new_process.get_pid()

    def load_to_memory(self, pid):
        """Adds the process to the ready queue and updates available memory if there is enough space"""
        if self.processes[pid].get_memory() < self.memory_available:
            self.processes[pid].set_ready()
            self.ready_queue.append(self.processes[pid])
            self.memory_available -= self.processes[pid].get_memory()
            print("Process %d loaded into memory" % pid)
            return True
        else:
            print("Process %d is waiting for memory to become available" % pid)
            return False

    def scheduler(self):
        """Scheduling algorithm using Round Robin"""
        while len(self.ready_queue) > 0:
            process = self.ready_queue.pop(0)
            self.semaphore.acquire(blocking=False)    # Allows 4 threads to run simultaneously
            try:
                process.set_run()
                pid = process.get_pid()
                t = Thread(target=self.run_process, args=(pid,))
                t.start()
            finally:
                self.semaphore.release()

    def load_ready_queue(self):
        for process in self.new_queue:
            # Loads all the new processes into memory until it is full
            with self.memory_condition:
                #  If there isn't enough room, wait until there is
                while not self.load_to_memory(process.get_pid()):
                    self.memory_condition.wait()

    def run_process(self, pid):
        """Runs the process and implements critical section resolving scheme"""
        operation = self.processes[pid].operations.pop(0)

        #  Critical Section resolving scheme
        if operation.is_critical():
            with self.critical_lock:  # Ensures no other process is in its critical section
                print("Running Process %d's critical %s operation" % (pid, operation.get_name()))
                self.run_op(pid, operation)
        else:
            print("Running Process %d: %s operation" % (pid, operation.get_name()))
            self.run_op(pid, operation)

        #  If there are no more operations to run, exit
        if len(self.processes[pid].operations) == 0:
            self.processes[pid].set_exit()
            self.memory_available += self.processes[pid].get_memory()  # Free up memory
            print("Process %d has finished execution in %f CPU cycles" % (pid, self.processes[pid].get_clock_time()))
            self.memory_condition.acquire()
            self.memory_condition.notify()        # Notifies the condition variable that more memory is available
            self.memory_condition.release()

        #  Else, re-add the process to the ready queue for scheduling
        else:
            self.ready_queue.append(self.processes[pid])
            t = Thread(target=self.scheduler())
            t.start()

    def run_op(self, pid, operation):
        """Determines operation type and executes it"""
        duration = operation.get_cycle_length()
        if operation.get_name() == "CALCULATE":
            #  Determine whether the operation will finish within the time slice
            if duration <= self.time_slice:
                self.occupy_cpu(pid, duration)
            else:  # Operation won't finish
                duration = self.time_slice
                self.occupy_cpu(pid, duration)
                operation.decrement_cycle_length(duration)  # Update remaining duration
                self.processes[pid].operations.insert(0, operation)  # Re-add operation to process
        elif operation.get_name() == "I/O":
            self.interrupt(pid, duration)
        elif operation.get_name() == "FORK":
            self.spawn_child(pid, duration)

    def occupy_cpu(self, pid, duration):
        """Simulate occupation of the CPU for the given duration"""
        count = duration
        while count > 0:
            time.sleep(.01)
            self.processes[pid].increment_clock_time(1)  # Updates process's PCB
            #  Fixed probability of eternal I/O event
            if random.random() <= 0.01:  # 1% chance
                self.interrupt(pid, random.randint(1, 10))  # interrupt the process for up to 10 seconds
                print("Process %d is interrupted" % pid)
            count -= 1

    def interrupt(self, pid, duration):
        """Sets the process state to wait and simulates the time for I/O operation"""
        self.processes[pid].set_wait()
        time.sleep(duration * 0.01)  # Simulate the time for device driver to perform I/O operation
        print("Process %d finished I/O operation in %f seconds" % (pid, duration))

    def spawn_child(self, pid, duration):
        """Sets the process state to wait and spawns a new child process"""
        self.processes[pid].set_wait()
        child_pid = self.generate_from_file('templates/program_file.xml')
        print("Process %d spawned from parent and added to new queue" % child_pid)
        time.sleep(duration * 0.01)

    def get_process_id(self, process):
        return self.processes.index(process)

    def print(self):
        for p in self.processes:
            print("\nProcess #", self.get_process_id(p))
            for o in p.operations:
                operation_name = o.get_name()
                operation_cycle_length = str(o.get_cycle_length())
                s = "%10s:\t%s" % (operation_name, operation_cycle_length)
                print(s.center(20, ' '))
