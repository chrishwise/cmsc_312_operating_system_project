import random
import threading

from process import Process
from operation import Operation
from xml.etree import ElementTree
from threading import *
import time


class CpuCore:
    time_slice = 30

    def __init__(self, window):
        self.window = window
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
        """Parses the given file and adds all of its operations to a new process and adds it to processes list"""
        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        operations = root.findall('operation')
        memory = int(root.find('memory').text)
        new_process = Process(self.pid_counter, memory)
        for o in operations:
            critical = False        # Bug fix. critical must be set false for each operation
            name = o.text.strip()
            has_critical = o.find('critical')
            if not (has_critical is None):    # Bug fix. Element.find() returns None when not found
                critical = True
            min_time = int(o.find('min').text)
            max_time = int(o.find('max').text)
            new_operation = Operation(name, min_time, max_time, critical)
            new_process.add_operation(new_operation)
        self.processes.append(new_process)
        self.new_queue.append(new_process)
        self.window.add_process(self.pid_counter)    # Adds the process to the process frame in AppWindow
        self.pid_counter += 1
        return new_process.get_pid()

    def load_to_memory(self, pid):
        """Adds the process to the ready queue and updates available memory if there is enough space"""
        if self.processes[pid].get_memory() < self.memory_available:
            self.processes[pid].set_ready()
            self.processes[pid].print()     # DEBUG
            self.ready_queue.append(self.processes[pid])
            self.memory_available -= self.processes[pid].get_memory()
            self.window.log(f"\nProcess {pid} loaded into memory")

            return True
        else:
            self.window.log(f"\nProcess {pid} is waiting for memory to become available")
            return False

    def load_ready_queue(self):
        """Loads processes from new queue into ready queue until it is full. Then begins scheduling"""
        while True:
            # Interprocess communication method using shared data.
            # All processes share queues, semaphores, condition variables, and locks
            time.sleep(.01)
            if len(self.new_queue) > 0:
                #  Semaphore allow up to 4 threads to run concurrently.
                with self.semaphore:
                    process = self.new_queue.pop(0)
                    # Interprocess communication using message passing.
                    with self.memory_condition:
                        #  If there isn't enough room, wait until another thread notifies itself exiting memory
                        while not self.load_to_memory(process.get_pid()):
                            self.memory_condition.wait()
                    t = Thread(target=self.scheduler)
                    t.start()

    def scheduler(self):
        """Scheduling algorithm using Round Robin"""
        while len(self.ready_queue) > 0:
            process = self.ready_queue.pop(0)           # Removes the first process from ready queue
            pid = process.get_pid()                     # Need pid to identify process
            self.processes[pid].set_run()
            self.window.set_running(pid)                # Update process's state
            self.run_process(pid)                       # Run the process

    def run_process(self, pid):
        """Runs the process and implements critical section resolving scheme"""
        operation = self.processes[pid].operations.pop(0)

        #  Critical Section resolving scheme
        if operation.is_critical():
            with self.critical_lock:  # Ensures no other process is in its critical section
                self.window.log(f"\nRunning Process {pid}'s critical {operation.get_name()} operation")
                self.run_op(pid, operation)
        else:
            self.window.log("\nRunning Process %d: %s operation" % (pid, operation.get_name()))
            self.run_op(pid, operation)

        #  If there are no more operations to run, exit
        if len(self.processes[pid].operations) == 0:
            self.processes[pid].set_exit()
            self.memory_available += self.processes[pid].get_memory()  # Free up memory
            self.window.set_finished(pid)            # Updates color in processes frame
            self.window.log(f"\nProcess {pid} has finished execution in {self.processes[pid].get_clock_time()} CPU cycles")
            with self.memory_condition:
                self.memory_condition.notify()  # Notifies the condition variable that more memory is available

        #  Else, re-add the process to the ready queue for scheduling
        else:
            self.ready_queue.append(self.processes[pid])

    def run_op(self, pid, operation):
        """Determines operation type and executes it. Uses Round Robin algorithm"""
        duration = operation.get_cycle_length()
        if operation.get_name() == "CALCULATE":
            #  Determine whether the operation will finish within the time slice
            if duration <= self.time_slice:
                self.occupy_cpu(pid, duration)
                self.window.log(f"\nProcess {pid} finished CALCULATE operation")
            else:  # Operation won't finish
                duration = self.time_slice
                self.occupy_cpu(pid, duration)
                operation.decrement_cycle_length(duration)  # Update remaining duration
                self.processes[pid].operations.insert(0, operation)  # Re-add operation to process
        elif operation.get_name() == "I/O":
            self.interrupt(pid, duration)
            self.window.log(f"\nProcess {pid} finished I/O operation")
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
                self.interrupt(pid, random.randint(1, 10))  # interrupt the process for up to 0.10 seconds
                self.window.log(f"\nProcess {pid} is interrupted")
            count -= 1

    def interrupt(self, pid, duration):
        """Sets the process state to wait and simulates the time for I/O operation"""
        self.processes[pid].set_wait()
        self.window.set_waiting(pid)
        time.sleep(duration * 0.01)  # Simulate the time for device driver to perform I/O operation

    def spawn_child(self, pid, duration):
        """Sets the process state to wait and spawns a new child process"""
        self.processes[pid].set_wait()
        self.window.set_waiting(pid)
        child_pid = self.generate_from_file('templates/program_file.xml')
        self.window.log(f"\nProcess {child_pid} spawned from parent and added to new queue")
        time.sleep(duration * 0.01)

    def get_process_id(self, process):
        return self.processes.index(process)

    def print(self):
        """Prints the processes with their operation list and CPU times"""
        for p in self.processes:
            print("\nProcess #", self.get_process_id(p))
            for o in p.operations:
                operation_name = o.get_name()
                operation_cycle_length = str(o.get_cycle_length())
                s = "%10s:\t%s" % (operation_name, operation_cycle_length)
                print(s.center(20, ' '))
