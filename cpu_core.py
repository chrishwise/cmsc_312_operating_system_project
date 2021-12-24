import random
import threading
from process import Process
from operation import Operation
from threading import *
import time
from main_memory import *


class CpuCore:
    time_slice = 30

    def __init__(self, window, storage):
        """Initializes Cpu Core"""
        self.window = window
        self.storage = storage
        # Interprocess communication method using shared data.
        # All processes share queues, semaphores, condition variables, and locks
        self.ready_queue = []   # Register for storing process data and instruction
        self.waiting_queue = []
        self.critical_lock = Lock()
        self.semaphore = Semaphore(4)
        self.pid_counter = 0
        # Initialize main memory
        self.memory = MainMemory(self.window, self.storage, self)

    def connect_memory(self, memory):
        """This function must be called before scheduler"""
        self.memory = memory

    def scheduler(self):
        """Scheduling algorithm using Round Robin"""
        while True:
            # Infinite loop waits until ready queue has a process before continuing
            time.sleep(0.01)
            if len(self.ready_queue) > 0:
                #  Semaphore allows up to 4 threads to run concurrently.
                with self.semaphore:
                    process = self.ready_queue.pop(0)           # Removes the first process from ready queue
                    pid = process.get_pid()                     # Need pid to identify process
                    self.storage.processes[pid].set_run()       # Update process's state
                    self.window.set_running(pid)                # Update GUI
                    self.run_process(pid)                       # Run the process

    def run_process(self, pid):
        """Runs the process and implements critical section resolving scheme"""
        operation = self.storage.processes[pid].operations.pop(0)

        #  Critical Section resolving scheme
        if operation.is_critical():
            with self.critical_lock:  # Ensures no other process is in its critical section
                self.window.log(f"\nRunning Process {pid}'s critical {operation.get_name()} operation")
                self.run_op(pid, operation)
        else:
            self.window.log("\nRunning Process %d: %s operation" % (pid, operation.get_name()))
            self.run_op(pid, operation)

        #  If there are no more operations to run, exit
        if len(self.storage.processes[pid].operations) == 0:
            self.storage.processes[pid].set_exit()
            self.memory.free_memory(pid)             # Free up memory
            self.window.set_finished(pid)            # Update GUI
            self.window.log(f"\nProcess {pid} has finished execution in "
                            f"{self.storage.processes[pid].get_clock_time()} CPU cycles")
            with self.memory.memory_condition:
                self.memory.memory_condition.notify()  # Notifies the condition variable that more memory is available

        #  Else, re-add the process to the ready queue for scheduling
        else:
            self.ready_queue.append(self.storage.processes[pid])

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
                self.storage.processes[pid].operations.insert(0, operation)  # Re-add operation to process
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
            self.storage.processes[pid].increment_clock_time(1)  # Updates process's PCB

            #  Fixed probability of eternal I/O event
            if random.random() <= 0.01:  # 1% chance
                self.interrupt(pid, random.randint(1, 10))  # interrupt the process for up to 0.10 seconds
                self.window.log(f"\nProcess {pid} is interrupted")
            count -= 1

    def interrupt(self, pid, duration):
        """Sets the process state to wait and simulates the time for I/O operation"""
        self.storage.processes[pid].set_wait()
        self.window.set_waiting(pid)
        time.sleep(duration * 0.01)  # Simulate the time for device driver to perform I/O operation

    def spawn_child(self, pid, duration):
        """Sets the process state to wait and spawns a new child process"""
        self.storage.processes[pid].set_wait()
        self.window.set_waiting(pid)
        # Parent-child management
        # Multi-level parent-child relationship. Program file 3 spawns program file 2 which spawns program file 1
        if self.storage.processes[pid].file_name == 'templates/program_file_2.xml':
            child_pid = self.storage.generate_from_file('templates/program_file.xml')
        elif self.storage.processes[pid].file_name == 'templates/program_file_3.xml':
            child_pid = self.storage.generate_from_file('templates/program_file_2.xml')
        self.storage.processes[pid].add_child(self.storage.processes[child_pid])
        self.window.update_child(child_pid, pid)   # update GUI

        self.window.log(f"\nProcess {child_pid} spawned from parent and added to new queue")
        time.sleep(duration * 0.01)

    def get_process_id(self, process):
        return self.storage.processes.index(process)

    def print(self):
        """Prints the processes with their operation list and CPU times"""
        for p in self.storage.processes:
            print("\nProcess #", self.get_process_id(p))
            for o in p.operations:
                operation_name = o.get_name()
                operation_cycle_length = str(o.get_cycle_length())
                s = "%10s:\t%s" % (operation_name, operation_cycle_length)
                print(s.center(20, ' '))
