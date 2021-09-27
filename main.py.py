import os
from xml.etree import ElementTree

class operation(object):

	def __init__(self, operation, min_time, max_time, critical):
		operation_name = operation
		self.min_time = min_time
		self.max_time = max_time
		self.critical = critical
		cycle_length = random.randrange(min_time, max_time, 1)

	def get_cycle_len(self):
		return self.cycle_length


class process(object):
	
	#pointer
	#process_state
	#process_num
	#program_counter
	#registers
	#memory_limits
	#open_file_lists

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


class processes:

	def __init__(self):
		self.processes = []

	def generate_from_file(self, file_name, num_processes):
		tree = ElementTree.parse(file_name)
		root = tree.getroot()
		template = root.find('template')
		critical_sections = template.findall('critical-section')
		non_critical_operations = template.findall('operation')
		p = 0
		while (p < num_processes):
			new_process = process()
			for cs in critical_sections:
				operations = cs.findall('operation')
				for o in operations:
					operation = o.find('name').text
					min_time = o.find('min').text
					max_time = o.find('max').text
					new_operation = operation(operation, min_time, max_time, True)
					new_process.add_operation(new_operation)
			for o in non_critical_operations:
				operation = o.find('name').text
				min_time = o.find('min').text
				max_time = o.find('max').text
				new_operation = operation(operation, min_time, max_time, False)
				new_process.add_operation(new_operation)
			self.processes.append(new_process)

num_processes = input('Select the number of processes to generate: ')
file_to_use = input('Select from available templates. Enter 1 or 2: ')
if(file_to_use == 1)
	file_name = 'program_file.xml'
else if (file_to_use == 2)
	file_name = 'program_file_2.xml'
ps = processes()
ps.generate_from_file(file_name, num_processes)
for p in processes:
	p.print()




			
		

