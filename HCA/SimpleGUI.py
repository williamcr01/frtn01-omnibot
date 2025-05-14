import threading
import tkinter as tk
from tkinter import ttk

class GainUI(threading.Thread):
    def __init__(self, PI):
        super().__init__(daemon=True)
        self.start()

    def run(self):
        self.root = tk.Tk()
        self.root.title("PI Controller Gains")

        self.entries = {}
        labels = ['KpX', 'KpY', 'KpTheta', 'KiX', 'KiY', 'KiTheta']

        for i, label in enumerate(labels):
            ttk.Label(self.root, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(self.root, width=6)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = entry

        ttk.Button(self.root, text="Submit", command=self.submit).grid(row=6, column=0, pady=10)
        ttk.Button(self.root, text="Exit", command=self.root.quit).grid(row=6, column=1, pady=10)

        self.root.mainloop()

    def submit(self):
        print("Submitted gains:")
        for label, entry in self.entries.items():
            value = entry.get()
            print(f"{label}: {value}")

def main():
    print("Main thread is running...")
    gui = GainUI(PI=None)

    import time
    for i in range(10):
        print(f"Main thread work... {i}")
        time.sleep(1)

    print("Main thread done.")

main()