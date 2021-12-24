from xml.etree import ElementTree
from process import Process
from operation import Operation


class Storage:

    def __init__(self, window):
        self.window = window
        self.pid_counter = 0
        self.processes = []         # All processes
        self.new_queue = []         # Processes in storage
        self.address_pointer = 4096  # Keeps track of physical address

    def generate_from_file(self, file_name):
        """Parses the given file and adds all of its operations to a new process and adds it to processes list"""
        # Parse template file
        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        operations = root.findall('operation')
        memory = int(root.find('memory').text)

        # Generate physical address
        process_pointer = self.address_pointer
        self.address_pointer += memory
        new_process = Process(self.pid_counter, memory, process_pointer, file_name)

        for o in operations:
            critical = False  # Bug fix. critical must be set false for each operation
            name = o.text.strip()
            has_critical = o.find('critical')
            if not (has_critical is None):  # Bug fix. Element.find() returns None when not found
                critical = True
            min_time = int(o.find('min').text)
            max_time = int(o.find('max').text)
            new_operation = Operation(name, min_time, max_time, critical)
            new_process.add_operation(new_operation)
        self.processes.append(new_process)
        self.new_queue.append(new_process)
        self.window.add_process(self.pid_counter)  # Adds the process to the process frame in AppWindow
        self.pid_counter += 1
        return new_process.get_pid()
