# cmsc_312_operating_system_project
Project for CMSC 312

Phase 1:

I created classes for operation, process, and processes.
I used an object oriented approach to allow processes to be generated
I combined all of these classes into main.py

I tried to implement Round Robin but couldn't get it to fully work due to difficulties with setting burst time vs arrival time

Select the number of processes to generate: 
Select from available templates. Enter 1 or 2:

Processes are generated from xml template and then printed

Round robin is called to print but I have been struggling with getting it to work properly. Tried to implement it so that only critical sections need to be evaluated for scheduling.

Phase 2:
Completely redid all of my scheduler
Added multi-threading functionality using pythons threading module
Used semaphore with initial value 4 to simulate 4 threads of a CPU
Used a lock for critical section resolving scheme
Added memory to the template files and added functionality to load new process's to the ready queue
Struggling to debug after finally finishing all of Phase 2's required functionality

USER INSTRUCTIONS:
run main.py
follow the prompts to generate and run processes
