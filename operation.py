import random

class operation(object):

	operation_name
	int min_time
	int max_time
	int cycle_length
	critical 

	def __init__(self, operation, min_time, max_time, critical):
		operation_name = operation
		self.min_time = min_time
		self.max_time = max_time
		self.critical = critical
		cycle_length = random.randrange(min_time, max_time, 1)

	def get_cycle_len(self):
		return self.cycle_length