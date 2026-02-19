import psutil
import datetime
import os
import platform
import getpass
import socket
import glob


OUTPUT_DIR = "triage_reports"
# output_dir stores the folder name where reports will be saved

TIMESTAMP = datetime.datetime.now().strftime("%m%d%Y_%H%M%S")
# timestamp stores current date and time
# .strftime() String Format Time - converts time to readable text


# Create Report Structure
def create_report_structure():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print(f"[*] Starting Triage Collection at {TIMESTAMP}")

# Network COnnection
def get_network_connections():
    print("[*] Scanning Network Connections...")
    filename = f"{OUTPUT_DIR}/network_connections_{TIMESTAMP}.txt"
    try:
        with open(filename, "w") as f:
            f.write(f"Active Connections Scan - {TIMESTAMP}\n")
            f.write("="*60+"\n")
            for conn in psutil.net_connections(kind='inet'):
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                f.write(f"PID: {conn.pid} | Status: {conn.status} | Local: {laddr} -> Remote: {raddr}\n")
        print(f"[+] Network data saved to {filename}")
    except PermissionError:
        print("[!] Warning: Need administrator privileges for complete network data.")
    except Exception as e:
        print(f"[!] Error collecting network data: {e}")

# Running Processes
def get_running_processes():
    print("[*] Listing Running Processes...")
    filename = f"{OUTPUT_DIR}/process_list_{TIMESTAMP}.txt"
    with open(filename, "w") as f:
        f.write(f"Process List Scan - {TIMESTAMP}\n")
        f.write("="*60 + "\n")
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                f.write(f"PID: {proc.info['pid']} | User: {proc.info['username']} | Name: {proc.info['name']}\n")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    print(f" [+] Process data saved to {filename}")

# System Info
def get_system_info():
    print("[*] Collecting System Information...")
    filename = f"{OUTPUT_DIR}/system_info_{TIMESTAMP}.txt"
    with open(filename, "w") as f:
        f.write(f"System Information - {TIMESTAMP}\n")
        f.write("="*60 +"\n")
        f.write(f"Hostname: {socket.gethostname()}\n")
        f.write(f"Current User: {getpass.getuser()}\n")
        f.write(f"Operating System: {platform.system()}\n")
        f.write(f"OS Version: {platform.version()}\n")
        f.write(f"OS Release: {platform.release()}\n")
        f.write(f"Machine Type: {platform.machine()}\n")
        f.write(f"Processor: {platform.processor()}\n")
    print(f"[+] System Information saved to {filename}")

# StartUp Programs
def get_startup_programs():
    print("[*] Scanning Startup Programs...")
    filename = f"{OUTPUT_DIR}/startup_programs_{TIMESTAMP}.txt"
    try:
        import winreg
        with open(filename, "w") as f:
            f.write(f"Startup Programs - {TIMESTAMP}\n")
            f.write("="*60 + "\n")
            startup_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]
            for hkey, path in startup_keys:
                try:
                    f.write(f"\n[{path}]\n")
                    key = winreg.OpenKey(hkey, path)
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            f.write(f" {name}: {value}\n")
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    f.write(f" [Key not found]\n")
        print(f"[+] Startup Programs saved to {filename}")
    except ImportError:
        print("[!] Startup Program enumeration only suported on Windows")
    except Exception as e:
        print(f"[!] Error collecting startup Programs")

# Temp Files (Recently modified files. Malware likes to pop in here sometimes..) 
def get_temp_files():
    print("[*] Scanning Recent Temp Files...")
    filename = f"{OUTPUT_DIR}/recent_temp_files_{TIMESTAMP}.txt"
    import time
    with open(filename, "w") as f:
        f.write(f"Recent Temp Files (Last 24 Hours) - {TIMESTAMP}\n")
        f.write("="*60 + "\n")
        temp_dirs = []
        if platform.system() == "Windows":
            import os
            temp_dirs = [
                os.environ.get('TEMP', 'C:\\Windows\\Temp'),
                os.environ.get('TMP', 'C:\\Windows\\Temp'),
                'C:\\Windows\\Temp'
            ]
        else: # Linux or Mac
            temp_dirs = ['/tmp', '/var/tmp']
        current_time = time.time()
        for temp_dir in temp_dirs:
            try:
                f.write(f"\n[Scanning: {temp_dir}]\n")
                files = glob.glob(os.path.join(temp_dir, '*')) #glob.glob finds all files matching a pattern
                recent_files = []
                for file in files:
                    try:
                        if os.path.isfile(file):






if __name__ == "__main__":
    create_report_structure()
    get_network_connections()
    get_running_processes()
    get_system_info()
    get_startup_programs()
    print("[+] Triage Complete.")