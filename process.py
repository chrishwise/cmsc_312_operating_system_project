import process_control_block as pcb


class Process(object):

	def __init__(self, pid, memory):
		memory_req = memory
		clock_time_elapsed = 0
		pc = 0
		pointer = 0
		registers = []
		process_state = "NEW"
		self.pcb = pcb.ProcessControlBlock(pointer, process_state, pid, pc, registers, memory_req, clock_time_elapsed)
		self.operations = []

	def add_operation(self, operation):
		self.operations.append(operation)

	def is_new(self):
		if self.pcb.state == "NEW":
			return True
		else:
			return False

	def set_ready(self):
		self.pcb.state = "READY"

	def is_ready(self):
		if self.pcb.state == "READY":
			return True
		else:
			return False

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

	def set_program_counter(self, address):
		self.pcb.program_counter = address

	def get_time_required(self):
		seconds = 0
		for o in self.operations:
			seconds += o.get_cycle_length()
		return seconds

	def print(self, pid):
		"""Prints the process's'operations and CPU times"""
		print("Process #", pid)
		for o in self.operations:
			operation_name = o.get_name()
			operation_cycle_length = str(o.get_cycle_length())
			if o.is_critical():
				s = f"critical {operation_name}:\t {operation_cycle_length}"
			else:
				s = f"\t{operation_name}:\t {operation_cycle_length}"
			print(s)

