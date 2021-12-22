import time
from random import random
from threading import Lock, Condition, Semaphore, Thread
from xml.etree import ElementTree

from cpu_core import CpuCore
from operation import Operation
from process import Process


class PriorityCpuCore(CpuCore):

    def __init__(self, window):
        CpuCore.__init__(self, window)
        self.priority_queue = []
        self.prioritize_processes()

    def prioritize_processes(self):
        self.priority_queue = sorted(self.new_queue, key=lambda p: p.get_time_required())

    def generate_from_file(self, file_name):
        """Parses the given file and adds all of its operations to a new process and adds it to processes list"""
        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        operations = root.findall('operation')
        memory = int(root.find('memory').text)
        new_process = Process(self.pid_counter, memory, file_name)
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
        # Sorts the list based on time required to implement shortest job first
        self.prioritize_processes()
        self.window.add_process(self.pid_counter)    # Adds the process to the process frame in AppWindow
        self.pid_counter += 1
        return new_process.get_pid()

    def run_op(self, pid, operation):
        """Determines operation type and executes it. Uses Shortest Job First algorithm"""
        duration = operation.get_cycle_length()
        if operation.get_name() == "CALCULATE":
            #  Determine whether the operation will finish within the time slice
            self.occupy_cpu(pid, duration)
            self.window.log(f"\nProcess {pid} finished CALCULATE operation")
        elif operation.get_name() == "I/O":
            self.interrupt(pid, duration)
            self.window.log(f"\nProcess {pid} finished I/O operation")
        elif operation.get_name() == "FORK":
            self.spawn_child(pid, duration)

