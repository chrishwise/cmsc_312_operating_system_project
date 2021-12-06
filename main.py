from cpu_core import *
from threading import *


cpu = CpuCore()
np = int(input('Select the number of processes to generate, or zero to quit: '))
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
print("\nLoading generated processes into main memory")
load_thread = Thread(target=cpu.load_ready_queue())
load_thread.start()
print("Beginning to schedule processes for execution\n")
cpu.scheduler()
