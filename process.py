import os
import random

class process(object):

	operations
	
	pointer
	process_state
	process_num
	program_counter
	registers
	memory_limits
	open_file_lists

	def __init__(self):
		self.operations = []
		self.process_state = 'NEW'
	
	def add_operation(self, operation):
		self.operations.append(operation)

	def print(self):
		print("Process #")
		for o in self.operations:
			print(o + ":    " + o.cycle_length)

	def set_ready(self):
		self.process_state = "READY"

	def set_run(self):
		self.process_state = "RUN"
		
