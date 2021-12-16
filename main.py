from cpu_core import *
from threading import *
import tkinter as tk
import tkinter.scrolledtext as ttk

root = tk.Tk()


class AppWindow(tk.Frame):

    def __init__(self, master=root):
        # Create a new window
        super(AppWindow, self).__init__(master)
        root.title("Operating System Simulator")
        root.rowconfigure([0, 1, 2, 3, 4], minsize=50, weight=1)
        root.columnconfigure([0, 1, 2], minsize=50, weight=1)

        # Initialize the CPU (1 core, 4 threads)
        self.cpu = CpuCore(self)

        # Create buttons for available templates
        self.label = tk.Label(text="Click on a template to create new processes")
        self.label.grid(row=0, column=0, columnspan=3)

        self.pf_1_btn = tk.Button(master=root, text="Program File One",
                                  command=lambda: self.cpu.generate_from_file('templates/program_file.xml'))
        self.pf_1_btn.grid(row=1, column=0)
        self.pf_2_btn = tk.Button(master=root, text="Program File Two",
                                  command=lambda: self.cpu.generate_from_file('templates/program_file_2.xml'))
        self.pf_2_btn.grid(row=1, column=1)
        self.pf_3_btn = tk.Button(master=root, text="Program File Three",
                                  command=lambda: self.cpu.generate_from_file('templates/program_file_3.xml'))
        self.pf_3_btn.grid(row=1, column=2)

        # Create a frame to display created processes
        self.processes_frame = tk.Frame(master=root, width=100, height=10, relief=tk.SUNKEN)
        self.processes_frame.grid(row=2, column=0, columnspan=3)

        # Create a button to run processes
        self.run_btn = tk.Button(master=root, text="Run", command=self.run)
        self.run_btn.grid(row=3, column=1)

        # Create a console window for output
        self.console = ttk.ScrolledText(master=root, relief=tk.SUNKEN)
        self.console.grid(row=4, column=0, columnspan=3)

        root.mainloop()

    def run(self):
        thread = Thread(target=self.cpu.load_ready_queue())
        thread.start()
        thread.join()

    def add_process(self, pid):
        p = tk.Text(master=self.processes_frame, width=10, height=5)
        p.insert(1.0, f"Process {pid}")
        p.pack(side=tk.LEFT)

    def log(self, string):
        self.console.insert('end', string)
        print(string)


application = AppWindow(root)
application.mainloop()


