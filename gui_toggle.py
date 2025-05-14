import tkinter as tk
import subprocess
import psutil
import os
import signal

# Script and batch file
SCRIPT_NAME = "main.py"
BATCH_FILE = os.path.join(os.path.dirname(__file__), "run_security.bat")  # Full path

def is_script_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any(SCRIPT_NAME in part for part in proc.info['cmdline']):
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def start_security():
    if not is_script_running():
        subprocess.Popen([BATCH_FILE], shell=True)
        status_label.config(text="🟢 Security system running.")
    else:
        status_label.config(text="⚠️ Security already running.")

def stop_security():
    pid = is_script_running()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            status_label.config(text="🔴 Security system stopped.")
        except Exception as e:
            status_label.config(text=f"❌ Error stopping: {e}")
    else:
        status_label.config(text="ℹ️ System is not running.")

# GUI
root = tk.Tk()
root.title("Security System Toggle")
root.geometry("300x160")

title = tk.Label(root, text="🔐 Laptop Security Control", font=("Arial", 14, "bold"))
title.pack(pady=10)

status_label = tk.Label(root, text="Status: Unknown", font=("Arial", 10))
status_label.pack(pady=5)

start_button = tk.Button(root, text="🟢 Start Security", command=start_security, width=25)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="🔴 Stop Security", command=stop_security, width=25)
stop_button.pack(pady=5)

root.mainloop()
