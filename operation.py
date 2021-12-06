import random


class Operation:

	def __init__(self, name, min_time, max_time, critical):
		self.operation_name = name
		self.min_time = min_time
		self.max_time = max_time
		self.critical = critical
		self.cycle_length = random.randrange(min_time, max_time, 1)

	def get_cycle_length(self):
		return self.cycle_length

	def decrement_cycle_length(self, decrement):
		self.cycle_length -= decrement

	def get_name(self):
		return self.operation_name

	def is_critical(self):
		return self.critical

