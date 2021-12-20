import time
from random import random
from threading import Lock, Condition, Semaphore, Thread


class PriorityCpuCore:

    def __init__(self, window, processes):
        self.window = window
        self.processes = processes
        self.new_queue = processes
        self.priority_queue = []
        self.waiting_queue = []
        self.exit_queue = []
        self.pid_counter = 0
        self.memory_available = 1024
        #self.memory_lock = Lock()
        self.memory_condition = Condition(self.memory_lock)
        self.critical_lock = Lock()
        self.semaphore = Semaphore(4)

    def prioritize_processes(self):
        self.priority_queue = sorted(self.processes, key=lambda p: p.get_time_required())

    def load_from_storage(self):
        while len(self.new_queue) > 0:
            process = self.new_queue.pop(0)
            with self.memory_condition:
                #  If there isn't enough room, wait until there is
                while not self.loaded(process.get_pid()):
                    self.memory_condition.wait()
            #  Allow 4 threads to run concurrently
            if self.semaphore.acquire(blocking=False):
                t = Thread(target=self.priority_scheduler())
                t.start()
                self.semaphore.release()

    def loaded(self, pid):
        """Returns True if the process gets loaded into memory"""
        if self.processes[pid].get_memory() < self.memory_available:
            self.processes[pid].set_ready()
            self.processes[pid].print(pid)  # DEBUG
            self.priority_queue.append(self.processes[pid])
            self.memory_available -= self.processes[pid].get_memory()
            self.window.log(f"\nProcess {pid} loaded into memory")
            return True
        else:
            self.window.log(f"\nProcess {pid} is waiting for memory to become available")
            return False

    def load_ready_queue(self):
        """Loads processes from new queue into ready queue until it is full. Then begins scheduling"""
        while len(self.new_queue) > 0:
            process = self.new_queue.pop(0)


    def priority_scheduler(self):
        """Scheduling algorithm using Priority Queue"""
        while len(self.priority_queue) > 0:
            process = self.priority_queue.pop()  # Removes the process with the highest priority (1 is highest)
            pid = process.get_pid()  # Need pid to identify process
            self.processes[pid].set_run()  # Update process's state
            self.run_process(pid)  # Run the process

    def run_process(self, pid):
        """Runs the process and implements critical section resolving scheme"""
        operation = self.processes[pid].operations.pop(0)

        #  Critical Section resolving scheme
        if operation.is_critical():
            with self.critical_lock:  # Ensures no other process is in its critical section
                self.window.log(
                    "\nRunning Process %d's critical %s operation" % (pid, operation.get_name()))
                self.run_op(pid, operation)
        else:
            self.window.log("\nRunning Process %d: %s operation" % (pid, operation.get_name()))
            self.run_op(pid, operation)

        #  If there are no more operations to run, exit
        if len(self.processes[pid].operations) == 0:
            self.processes[pid].set_exit()
            self.memory_available += self.processes[pid].get_memory()  # Free up memory
            self.window.log(
                f"\nProcess {pid} has finished execution in {self.processes[pid].get_clock_time()} CPU cycles")
            with self.memory_condition:
                self.memory_condition.notify()  # Notifies the condition variable that more memory is available

        #  Else, re-add the process to the ready queue for scheduling
        else:
            self.priority_queue.append(self.processes[pid])
            self.load_ready_queue()

    def run_op(self, pid, operation):
        """Determines operation type and executes it. Uses Round Robin algorithm"""
        duration = operation.get_cycle_length()
        if operation.get_name() == "CALCULATE":
            self.occupy_cpu(pid, duration)
            self.window.log(f"\nProcess {pid} finished CALCULATE operation")
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
        time.sleep(duration * 0.01)  # Simulate the time for device driver to perform I/O operation

    def spawn_child(self, pid, duration):
        """Sets the process state to wait and spawns a new child process"""
        self.processes[pid].set_wait()
        child_pid = self.generate_from_file('templates/program_file.xml')
        self.new_queue.append(self.processes[child_pid])
        self.window.log(f"\nProcess {pid} spawned from parent and added to new queue")
        time.sleep(duration * 0.01)

    def get_process_id(self, process):
        return self.processes.index(process)
