import os, random
from xml.etree import ElementTree

class Operation:

	def __init__(self, name, min_time, max_time, critical):
		self.operation_name = name
		self.min_time = min_time
		self.max_time = max_time
		self.critical = critical
		self.cycle_length = random.randrange(min_time, max_time, 1)

	def get_cycle_length(self):
		return self.cycle_length

	def get_name(self):
		return self.operation_name

class Process(object):
	
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

	def set_ready(self):
		self.process_state = "READY"

	def set_run(self):
		self.process_state = "RUN"

class Processes:

	def __init__(self):
		self.processes = []

	def generate_from_file(self, file_name, num_processes):
		tree = ElementTree.parse(file_name)
		root = tree.getroot()
		critical_sections = root.findall('critical-section')
		non_critical_operations = root.findall('operation')
		p = 0
		while (p < num_processes):
			new_process = Process()
			for cs in critical_sections:
				operations = cs.findall('operation')
				for o in operations:
					name = str(o.text)
					min_time = int(o.find('min').text)
					max_time = int(o.find('max').text)
					new_operation = Operation(name, min_time, max_time, True)
					new_process.add_operation(new_operation)
			for o in non_critical_operations:
				name = o.text
				min_time = int(o.find('min').text)
				max_time = int(o.find('max').text)
				new_operation = Operation(name, min_time, max_time, False)
				new_process.add_operation(new_operation)
			self.processes.append(new_process)
			p += 1

	def get_process_id(self, process):
		return self.processes.index(process)

	def print(self):
		for p in self.processes:
			print("Process #", self.get_process_id(p))
			for o in p:
				operation_name = o.get_name()
				operation_cycle_length = str(o.get_cycle_length())
				print('\t{0}:'.
					format(operation_name)),
				print('\t{0}'.
					format(operation_cycle_length))
		

class Round_Robin:

	def process_data(self, num_processes, process_id, arrival_time, burst_time, time_slice):
		process_id = process_id
		arrival_time = arrival_time
		burst_time = burst_time
		time_slice = time_slice
		process_data = []
		for i in range(num_processes):
			Round_Robin.scheduling_process(process_data, time_slice)

	def scheduling_process(self, process_data, time_slice):
		start_time = []
		exit_time = []
		executed_process = []
		ready_queue = []
		s_time = 0
		process_data.sort(key=lambda x: x[1])
		temp = []
		for i in range(len(process_data)):
			if process_data[i][1] <= s_time and process_data[i][3] == 0:
				present = 0
				if len(ready_queue) != 0:
					for k in range(len(ready_queue)):
						if process_data[i][0] == ready_queue:
							present = 1
				if present == 0:
	                    temp.extend([process_data[i][0], process_data[i][1], process_data[i][2], process_data[i][4]])
	                    ready_queue.append(temp)
	                    temp = []
	            if len(ready_queue) != 0 and len(executed_process) != 0:
	                    for k in range(len(ready_queue)):
	                        if ready_queue[k][0] == executed_process[len(executed_process) - 1]:
	                            ready_queue.insert((len(ready_queue) - 1), ready_queue.pop(k))
	            elif process_data[i][3] == 0:
	                temp.extend([process_data[i][0], process_data[i][1], process_data[i][2], process_data[i][4]])
	                normal_queue.append(temp)
	                temp = []
	        if len(ready_queue) == 0 and len(normal_queue) == 0:
	            break
	        if len(ready_queue) != 0:
	            if ready_queue[0][2] > time_slice:
	            	start_time.append(s_time)
	                s_time = s_time + time_slice
	                e_time = s_time
	                exit_time.append(e_time)
	                executed_process.append(ready_queue[0][0])
	                for j in range(len(process_data)):
	                    if process_data[j][0] == ready_queue[0][0]:
	                        break
	                process_data[j][2] = process_data[j][2] - time_slice
	                ready_queue.pop(0)
	            elif ready_queue[0][2] <= time_slice:
	            	start_time.append(s_time)
	                s_time = s_time + ready_queue[0][2]
	                e_time = s_time
	                exit_time.append(e_time)
	                executed_process.append(ready_queue[0][0])
	                for j in range(len(process_data)):
	                    if process_data[j][0] == ready_queue[0][0]:
	                        break
	                process_data[j][2] = 0
	                process_data[j][3] = 1
	                process_data[j].append(e_time)
	                ready_queue.pop(0)
	        elif len(ready_queue) == 0:
	            if s_time < normal_queue[0][1]:
	                s_time = normal_queue[0][1]
	            if normal_queue[0][2] > time_slice:
	                '''
	                If process has remaining burst time greater than the time slice, it will execute for a time period equal to time slice and then switch
	                '''
	                start_time.append(s_time)
	                s_time = s_time + time_slice
	                e_time = s_time
	                exit_time.append(e_time)
	                executed_process.append(normal_queue[0][0])
	                for j in range(len(process_data)):
	                    if process_data[j][0] == normal_queue[0][0]:
	                        break
	                process_data[j][2] = process_data[j][2] - time_slice
	            elif normal_queue[0][2] <= time_slice:
	            	start_time.append(s_time)
	                s_time = s_time + normal_queue[0][2]
	                e_time = s_time
	                exit_time.append(e_time)
	                executed_process.append(normal_queue[0][0])
	                for j in range(len(process_data)):
	                    if process_data[j][0] == normal_queue[0][0]:
	                        break
	                process_data[j][2] = 0
	                process_data[j][3] = 1
	                process_data[j].append(e_time)
	    t_time = RoundRobin.calculateTurnaroundTime(self, process_data)
	    w_time = RoundRobin.calculateWaitingTime(self, process_data)
	    RoundRobin.printData(self, process_data, t_time, w_time, executed_process)

	 def calculateTurnaroundTime(self, process_data):
	    total_turnaround_time = 0
	    for i in range(len(process_data)):
	        turnaround_time = process_data[i][5] - process_data[i][1]
	        total_waiting_time = total_waiting_time + waiting_time
	        process_data[i].append(waiting_time)
	    average_waiting_time = total_waiting_time / len(process_data)
	    return average_waiting_time

	def printData(self, process_data, average_turnaround_time, average_waiting_time, executed_process):
	    process_data.sort(key=lambda x: x[0])
	    print("Process_ID  Arrival_Time  Rem_Burst_Time   Completed  Original_Burst_Time  Completion_Time  Turnaround_Time  Waiting_Time")
	    for i in range(len(process_data)):
	        for j in range(len(process_data[i])):
	        	print(process_data[i][j], end="				")
	        print()
	        print(f'Average Turnaround Time: {average_turnaround_time}')
	        print(f'Average Waiting Time: {average_waiting_time}')
	        print(f'Sequence of Processes: {executed_process}')
	        if __name__ == "__main__":
			    no_of_processes = int(input("Enter number of processes: "))
			    rr = RoundRobin()
			    rr.processData(no_of_processes)



num_processes = input('Select the number of processes to generate: ')
file_to_use = input('Select from available templates. Enter 1 or 2: ')

if(file_to_use == 1):
	file_name = 'program_file.xml'
else:
	if (file_to_use == 2):
		file_name = 'program_file_2.xml'

ps = Processes()
ps.generate_from_file(file_name, num_processes)

rr = RoundRobin()
for p in ps.processes:
	p.print()
	if(p.get_critical == true):
		arrival_time = p.get_cycle_length
		process_id = ps.get_process_id(p)
		burst_time = p.get_cycle_length
		time_slice = 3
		rr.processData(len(ps.processes), process_id, arrival_time, burst_time, time_slice)
	





			
		

