import time
from random import random
from threading import Lock, Condition, Semaphore, Thread
from cpu_core import CpuCore


class PriorityCpuCore(CpuCore):

    def __init__(self, window):
        CpuCore.__init__(self, window)
        self.priority_queue = []
        self.prioritize_processes()

    def prioritize_processes(self):
        self.priority_queue = sorted(self.processes, key=lambda p: p.get_time_required())

    def priority_scheduler(self):
        """Scheduling algorithm using Priority Queue"""
        while len(self.priority_queue) > 0:
            process = self.priority_queue.pop()  # Removes the process with the highest priority (1 is highest)
            pid = process.get_pid()  # Need pid to identify process
            self.processes[pid].set_run()  # Update process's state
            self.run_process(pid)  # Run the process

