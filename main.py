import psutil
import datetime
import os

OUTPUT_DIR = "triage_reports"
# output_dir stores the folder name where reports will be saved

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# timestamp stores current date and time
# .strftime() String Format Time - converts time to readable text


# New function - Create Report Structure
def create_report_structure():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print(f"[*] Starting Triage Collection at {TIMESTAMP}")

# New function - Network COnnection
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

# New function - Running Processes
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

if __name__ == "__main__":
    create_report_structure()
    get_network_connections()
    get_running_processes()
    print("[+] Triage Complete.")