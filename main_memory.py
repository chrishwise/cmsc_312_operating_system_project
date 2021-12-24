import time
from threading import *


class MainMemory:

    def __init__(self, window, storage, cpu):
        # Memory Management
        self.window = window
        self.storage = storage
        self._memory_available = 1024    # main memory has a limit of 1024 MB
        self.memory_lock = Lock()
        self.memory_condition = Condition(self.memory_lock)

        # Paging implementation
        self.available_frames = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.frames = []
        self.page_number = 0

        # Initialize frame table
        for frame in range(16):
            self.frames.append(None)

        # Processes in memory
        self.ready_queue = []
        self.cpu = cpu

    def load_memory(self):
        """Loads processes from new queue (disk storage) onto ready queue (main memory). Infinite loop"""
        while True:
            time.sleep(.01)
            if len(self.storage.new_queue) > 0:
                process = self.storage.new_queue.pop(0)

                # Deadlock avoidance algorithm - resource request algorithm
                with self.memory_condition:     # Interprocess communication method using shared data.
                    # If there isn't enough room, wait until another thread notifies that it's exiting memory
                    while not self.loaded_to_memory(process.get_pid()):
                        self.memory_condition.wait()    # Interprocess communication using message passing
                # print(self.cpu.ready_queue)
                # t = Thread(target=self.cpu.scheduler)
                # t.start()

    def loaded_to_memory(self, pid):
        """Adds the process to the ready queue and updates available memory if there is enough space"""
        # Resource-request algorithm: check that requested resource is < available
        if self.storage.processes[pid].get_memory() < self.get_mem_available():
            # No swapping needed

            # Fill process's page table
            for page in range(self.storage.processes[pid].pages_needed):
                page_num = self.page_number
                self.storage.processes[pid].page_table.append((page_num, self.assign_frame(page_num)))
                self.page_number = (self.page_number + 1) % 16

            # Update process
            self.storage.processes[pid].set_ready()
            self.storage.processes[pid].print()     # DEBUG

            # Load process into memory
            self.cpu.ready_queue.append(self.storage.processes[pid])
            self._memory_available -= self.storage.processes[pid].get_memory()
            self.window.log(f"\nProcess {pid} loaded into memory")
            return True
        else:
            #
            self.window.log(f"\nProcess {pid} is waiting for memory to become available")
            return False

    def get_mem_available(self):
        return self._memory_available

    def free_memory(self, pid):
        self._memory_available += self.storage.processes[pid].get_memory()
        for entry_tuple in self.storage.processes[pid].page_table:
            frame_index = entry_tuple[1]
            self.frames[frame_index] = None
            self.available_frames.append(frame_index)
            self.window.update_page_table(frame_index, "None")

    def assign_frame(self, page_number):
        """Adds the page number to the frame table at the first available frame"""
        if len(self.available_frames) > 0:
            frame = self.available_frames.pop(0)
            self.frames[frame] = page_number
            self.window.update_page_table(frame, page_number)
            return frame
        else:
            print("NO AVAILABLE FRAMES")    # Debugging
            return None

    def remove_page(self, page_number):
        frame_index = self.get_frame(page_number)
        self.frames[frame_index] = 0
        self.available_frames.append(frame_index)

    def has_page(self, page_number):
        """Returns True if the page number is in the page table"""
        for frame in self.frames:
            if frame == page_number:
                return True
        return False

    def get_frame(self, page_number):
        for frame_index in range(len(self.frames)):
            if self.frames[frame_index] == page_number:
                return frame_index
        return 0

    def get_physical_address(self, page_number, offset):
        if self.has_page(page_number):
            return self.frame_size * self.get_frame(page_number) + offset


