import process_control_block as pcb


class Process(object):

	def __init__(self, pid, memory, pointer, fn):

		clock_time_elapsed = 0
		pc = 0
		registers = []
		process_state = "NEW"

		# Memory Management for paging implementation
		memory_req = memory								# Memory required by process
		page_size = 64 									# 64 MB, same as frame size in main memory
		self.pages_needed = memory_req // page_size		# number of entries in process' page table
		self.page_table = []

		self.pcb = pcb.ProcessControlBlock(pointer, process_state, pid, pc, registers, memory_req, clock_time_elapsed)
		self.operations = []
		self.children = []
		self.file_name = fn
		self.priority = 0

	def add_operation(self, operation):
		self.operations.append(operation)

	def set_ready(self):
		self.pcb.state = "READY"

	def set_run(self):
		self.pcb.state = "RUN"

	def set_wait(self):
		self.pcb.state = "WAIT"

	def set_exit(self):
		self.pcb.state = "EXIT"

	def get_pid(self):
		return self.pcb.pid

	def get_memory(self):
		return self.pcb.memory

	def increment_clock_time(self, increment):
		self.pcb.clock_time += increment

	def get_clock_time(self):
		return self.pcb.clock_time

	def get_time_required(self):
		seconds = 0
		for o in self.operations:
			seconds += o.get_cycle_length()
		return seconds

	def add_child(self, child_process):
		self.children.append(child_process)

	def print(self):
		print(f"\nProcess #{self.get_pid()}")
		print(f"Memory: {self.get_memory()}")
		for o in self.operations:
			if o.is_critical():
				print("Critical")
			operation_name = o.get_name()
			operation_cycle_length = str(o.get_cycle_length())
			s = "%10s:\t%s" % (operation_name, operation_cycle_length)
			print(s.center(20, ' '))


