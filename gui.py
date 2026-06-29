import os
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext


import main


class FirstResponseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("First Response Triage Tool")
        self.root.geometry("620x420")
        self.status_box = scrolledtext.ScrolledText(root, width=16, height=72)
        self.status_box.pack(padx=12, pady=12, fill="both", expand=True)
        self.run_button = tk.Button(root, text="Run Full Triage", command=self.run_triage_clicked)
        self.run_button.pack(padx=12, pady=4, fill="x")
        self.open_button = tk.Button(root, text="Open Reports Folder", command=self.open_reports_folder)
        self.open_button.pack(padx=12,pady=4, fill="x")
        
        self.write_status("Ready. Click Run Full Triage to start the collection process.\n")

    def write_status(self, message):
        self.status_box.insert(tk.END, message + "\n")
        self.status_box.see(tk.END)

    def run_triage_clicked(self):
        self.run_button.config(state=tk.DISABLED)
        self.write_status("Starting Triage Collection...\n")
        triage_thread = threading.Thread(target=self.run_triage_in_background)
        triage_thread.start()

    def run_triage_in_background(self):
        try:
            main.run_triage()
            self.write_status("Triage complete. Reports saved in triage_reports.\n")
        except Exception as e:
            messagebox.showerror(f"Error during triage", str(e))
            self.write_status(f"Error: {e}")
        finally:
            self.run_button.config(state="normal")
    
    def open_reports_folder(self):
        reports_path = os.path.abspath(main.OUTPUT_DIR)
        if not os.path.exists(reports_path):
            os.makedirs(reports_path)
            messagebox.showinfo("Info", "Reports folder does not exist yet.")
        if platform.system() == "Windows":
                os.startfile(reports_path)
        elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", reports_path])
        else:  # Linux and other OSes
                subprocess.Popen(["xdg-open", reports_path])

def main_window():
    root = tk.Tk()
    app = FirstResponseApp(root)
    root.mainloop()
    return app

if __name__ == "__main__":
    main_window()