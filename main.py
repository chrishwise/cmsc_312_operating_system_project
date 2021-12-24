from cpu_core import *
from threading import *
import tkinter as tk
import tkinter.scrolledtext as ttk
from storage import *
from main_memory import *


class AppWindow:

    def __init__(self):
        # Create a new window
        root = tk.Tk()
        # super(AppWindow, self).__init__(master)
        root.title("Operating System Simulator")

        # Initialize storage
        self.storage = Storage(self)

        # Initialize the CPU (1 core, 4 threads)
        self.cpu = CpuCore(self, self.storage)

        # Initialize main memory
        self.memory = MainMemory(self, self.storage, self.cpu)
        self.cpu.connect_memory(self.memory)

        # Initialize grid configuration for GUI
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Create buttons for available templates
        self.label = tk.Label(text="Click on a template to create new processes")
        self.label.grid(row=0, column=0, columnspan=3, padx=10, pady=10,)

        self.pf_1_btn = tk.Button(master=root, text="Program File One",
                                  command=lambda: self.storage.generate_from_file('templates/program_file.xml'))
        self.pf_1_btn.grid(row=1, column=0, pady=10,)
        self.pf_2_btn = tk.Button(master=root, text="Program File Two",
                                  command=lambda: self.storage.generate_from_file('templates/program_file_2.xml'))
        self.pf_2_btn.grid(row=1, column=1, pady=10)
        self.pf_3_btn = tk.Button(master=root, text="Program File Three",
                                  command=lambda: self.storage.generate_from_file('templates/program_file_3.xml'))
        self.pf_3_btn.grid(row=1, column=2, pady=10)

        # Create a frame to display created processes
        self.processes_frame = tk.Frame(master=root, width=1000, height=90, relief=tk.SUNKEN)
        self.processes_frame.grid_propagate(False)
        self.processes_frame.grid(row=2, column=0, columnspan=3)
        self.processes = []
        self.frames = []

        # Create a button to run processes
        self.run_btn = tk.Button(master=root, text="Run", command=self.run)
        self.run_btn.grid(row=3, column=1, pady=10)

        # Create a console window for output
        self.console = ttk.ScrolledText(master=root, relief=tk.SUNKEN)
        self.console.grid(row=4, column=0, columnspan=2)

        # Create a window for paging table
        self.paging_frame = tk.Frame(master=root, height=400, width=200, relief=tk.SUNKEN)
        self.paging_frame.grid(row=4, column=2)
        self.paging_frame.grid_columnconfigure(0, weight=1)
        self.paging_frame.grid_columnconfigure(1, weight=1)

        self.frame_nums = tk.Frame(master=self.paging_frame, width=100)
        self.frame_nums.config(background="black")
        self.frame_nums.grid(row=0, column=0)
        self.page_nums = tk.Frame(master=self.paging_frame, width=100)
        self.page_nums.config(background="black")
        self.page_nums.grid(row=0, column=1)
        self.page_entries = []
        for frame in range(16):
            table_entry = tk.Label(master=self.frame_nums, text=f"Frame {frame}", height=1, width=8)
            table_entry.config(background="white")
            table_entry.grid(row=frame, column=0, padx=1, pady=1)
        for page in range(16):
            page_entry = tk.Label(master=self.page_nums, text="None", height=1, width=12, padx=1, pady=1)
            page_entry.config(background="white")
            page_entry.grid(row=page, column=0, padx=1, pady=1)
            self.page_entries.append(page_entry)

        root.mainloop()

    def run(self):
        memory_thread = Thread(target=self.memory.load_memory)
        cpu_thread = Thread(target=self.cpu.scheduler)
        memory_thread.start()
        cpu_thread.start()

    def add_process(self, pid):
        # Create frame for border color
        f = tk.Frame(master=self.processes_frame, background="blue")
        # Create text inside frame
        p = tk.Text(master=f, width=10, height=5)
        p.insert(1.0, f"Process {pid}")
        p.pack(side=tk.LEFT, padx=1, pady=1)
        # Add frame to processes frame
        f.pack(side=tk.LEFT)
        self.processes.append(p)
        self.frames.append(f)

    def update_page_table(self, frame, page):
        self.page_entries[frame].config(text=f"Page {page}")

    def set_running(self, pid):
        self.frames[pid].config(background="green")

    def set_waiting(self, pid):
        self.frames[pid].config(background="yellow")

    def set_finished(self, pid):
        self.frames[pid].config(background="red")

    def log(self, string):
        self.console.insert('end', string)
        print(string)

    def update_child(self, child_pid, parent_pid):
        child_frame = self.processes[child_pid]
        child_frame.insert(2.0, f"\n\nParent: \nProcess {parent_pid}")


application = AppWindow()

