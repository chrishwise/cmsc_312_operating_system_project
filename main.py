from cpu_core import CpuCore


cpu = CpuCore()
np = int(input('Select the number of processes to generate, or zero to quit: '))
while np > 0:
    file_to_use = int(input('Select from available templates. Enter 1, 2, or 3: '))
    if file_to_use == 1 or file_to_use == 2:
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
print("\nBeginning to schedule processes for execution\n")
cpu.scheduler()
