from cpu_core import *
from threading import *

# Initialize the CPU (1 core, 4 threads)
cpu = CpuCore()
np = int(input('Select the number of processes to generate, or zero to quit: '))

#  Generate the inputted number of programs from template files
while np > 0:
    file_to_use = int(input('Select from available templates. Enter 1, 2, or 3: '))
    if file_to_use > 0:
        if file_to_use == 1:
            fn = 'templates/program_file.xml'
        elif file_to_use == 2:
            fn = 'templates/program_file_2.xml'
        elif file_to_use == 3:
            fn = 'templates/program_file_3.xml'

        cpu.generate_from_file(fn)
        np -= 1
    else:
        print("invalid template selection")
cpu.print()
print("\nRUNNING OS SIMULATOR\n")
print("Loading generated processes into main memory")
t = Thread(target=cpu.load_ready_queue())
#t2 = Thread(target=cpu.scheduler())
t.start()
#t2.start()
