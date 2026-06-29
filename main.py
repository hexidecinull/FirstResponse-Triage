import psutil
import csv
import datetime
import hashlib
import json
import os
import platform
import getpass
import shutil
import sqlite3
import socket
import tempfile
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
        one_day_seconds = 24 * 60 * 60
        for temp_dir in temp_dirs:
            try:
                f.write(f"\n[Scanning: {temp_dir}]\n")
                if not os.path.exists(temp_dir):
                    f.write(f" [Directory not found]\n")
                    continue
                files = glob.glob(os.path.join(temp_dir, '*')) #glob.glob finds all files matching a pattern
                recent_files = []
                for file in files:
                    try:
                        if os.path.isfile(file):
                            modified_time = os.path.getmtime(file)
                            file_age = current_time - modified_time
                            if file_age <= one_day_seconds:
                                readable_time = datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S") #Converts seconds into a normal date and time format. This was slightly confusing to do for the first time. lol)
                                file_size = os.path.getsize(file)
                                f.write(f" {file} | Size: {file_size} bytes | Last Modified: {readable_time}\n")
                                recent_files.append(file)
                    except (PermissionError, OSError) as e: #Windows/Linux blocks access to file. OSError catches other file issues.
                        f.write(f" Could not read file {file}: {e}\n") 
                if not recent_files:
                    f.write(" No recent files found in this directory.\n")
            except Exception as e:
                f.write(f" Error scanning directory {temp_dir}: {e}\n")
    print(f"[+] Recent Temp Files saved to {filename}")


# Roadmap Additions / Helper Functions
# These functions were added after the first simple triage collectors above.

def write_csv_report(filename, rows, fieldnames):
    # CSV means Comma-Separated Values; spreadsheet tools can open this format.
    # fieldnames controls the column names and the order they appear in.
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # DictWriter writes dictionaries into CSV rows.
        writer.writeheader()
        # writeheader() writes the first row with the column names.
        writer.writerows(rows)
        # writerows() writes every dictionary from the rows list.


def write_json_summary(filename, data):
    # JSON is structured text that other programs can easily read.
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        # indent=4 makes the JSON easier for humans to read.


def calculate_file_hashes(file_path):
    # A hash is a fingerprint for a file's contents.
    # MD5 is older and weaker, but still common in triage reports.
    # SHA256 is stronger and better for modern security work.
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # "rb" means read the file as raw bytes instead of normal text.
        while True:
            chunk = f.read(8192)
            # Reading in chunks avoids loading a huge file into memory at once.
            if not chunk:
                break
            md5_hash.update(chunk)
            sha256_hash.update(chunk)

    return {
        "md5": md5_hash.hexdigest(),
        "sha256": sha256_hash.hexdigest()
    }


def format_unix_time(timestamp):
    # Unix time is stored as seconds since January 1, 1970.
    return datetime.datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y %H:%M:%S")


def format_chromium_time(chromium_time):
    # Chrome and Edge store time as microseconds since January 1, 1601.
    if not chromium_time:
        return "N/A"
    seconds_since_1601 = chromium_time / 1000000
    seconds_between_1601_and_1970 = 11644473600
    unix_seconds = seconds_since_1601 - seconds_between_1601_and_1970
    return format_unix_time(unix_seconds)


def copy_database_to_temp(database_path):
    # Browsers can lock history databases while they are open.
    # Copying the database lets us read the copy without bothering the browser.
    temp_copy = tempfile.NamedTemporaryFile(delete=False)
    temp_copy.close()
    shutil.copy2(database_path, temp_copy.name)
    return temp_copy.name


def get_browser_history_paths():
    # This returns common browser history database locations for the current OS.
    system_name = platform.system()
    home_dir = os.path.expanduser("~")
    history_paths = []

    if system_name == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        app_data = os.environ.get("APPDATA", "")
        history_paths.extend([
            {
                "browser": "Chrome",
                "type": "chromium",
                "path": os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "History")
            },
            {
                "browser": "Edge",
                "type": "chromium",
                "path": os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "History")
            }
        ])
        firefox_pattern = os.path.join(app_data, "Mozilla", "Firefox", "Profiles", "*", "places.sqlite")
    elif system_name == "Darwin":
        history_paths.extend([
            {
                "browser": "Chrome",
                "type": "chromium",
                "path": os.path.join(home_dir, "Library", "Application Support", "Google", "Chrome", "Default", "History")
            },
            {
                "browser": "Edge",
                "type": "chromium",
                "path": os.path.join(home_dir, "Library", "Application Support", "Microsoft Edge", "Default", "History")
            }
        ])
        firefox_pattern = os.path.join(home_dir, "Library", "Application Support", "Firefox", "Profiles", "*", "places.sqlite")
    else:
        history_paths.extend([
            {
                "browser": "Chrome",
                "type": "chromium",
                "path": os.path.join(home_dir, ".config", "google-chrome", "Default", "History")
            },
            {
                "browser": "Edge",
                "type": "chromium",
                "path": os.path.join(home_dir, ".config", "microsoft-edge", "Default", "History")
            }
        ])
        firefox_pattern = os.path.join(home_dir, ".mozilla", "firefox", "*", "places.sqlite")

    for firefox_path in glob.glob(firefox_pattern):
        history_paths.append({
            "browser": "Firefox",
            "type": "firefox",
            "path": firefox_path
        })

    return history_paths


def collect_chromium_history(history_path, browser_name):
    rows = []
    temp_copy_path = copy_database_to_temp(history_path)
    try:
        connection = sqlite3.connect(temp_copy_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT url, title, visit_count, last_visit_time FROM urls "
            "ORDER BY last_visit_time DESC LIMIT 50"
        )
        for url, title, visit_count, last_visit_time in cursor.fetchall():
            rows.append({
                "browser": browser_name,
                "url": url,
                "title": title or "",
                "visit_count": visit_count,
                "last_visit_time": format_chromium_time(last_visit_time)
            })
        connection.close()
    finally:
        os.remove(temp_copy_path)
        # os.remove() deletes the temporary database copy after we finish reading it.
    return rows


def collect_firefox_history(history_path, browser_name):
    rows = []
    temp_copy_path = copy_database_to_temp(history_path)
    try:
        connection = sqlite3.connect(temp_copy_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT url, title, visit_count, last_visit_date FROM moz_places "
            "ORDER BY last_visit_date DESC LIMIT 50"
        )
        for url, title, visit_count, last_visit_date in cursor.fetchall():
            last_visit_time = "N/A"
            if last_visit_date:
                # Firefox stores this value as microseconds since January 1, 1970.
                last_visit_time = format_unix_time(last_visit_date / 1000000)
            rows.append({
                "browser": browser_name,
                "url": url,
                "title": title or "",
                "visit_count": visit_count,
                "last_visit_time": last_visit_time
            })
        connection.close()
    finally:
        os.remove(temp_copy_path)
    return rows


def get_browser_history():
    print("[*] Collecting Browser History...")
    filename = f"{OUTPUT_DIR}/browser_history_{TIMESTAMP}.txt"
    csv_filename = f"{OUTPUT_DIR}/browser_history_{TIMESTAMP}.csv"
    history_rows = []

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Browser History - {TIMESTAMP}\n")
        f.write("="*60 + "\n")
        for browser_info in get_browser_history_paths():
            browser_name = browser_info["browser"]
            browser_type = browser_info["type"]
            history_path = browser_info["path"]
            f.write(f"\n[{browser_name}: {history_path}]\n")

            if not os.path.exists(history_path):
                f.write(" History database not found.\n")
                continue

            try:
                if browser_type == "chromium":
                    rows = collect_chromium_history(history_path, browser_name)
                else:
                    rows = collect_firefox_history(history_path, browser_name)
                history_rows.extend(rows)
                for row in rows:
                    f.write(f" URL: {row['url']}\n")
                    f.write(f" Title: {row['title']}\n")
                    f.write(f" Visit Count: {row['visit_count']}\n")
                    f.write(f" Last Visit: {row['last_visit_time']}\n\n")
            except (PermissionError, OSError, sqlite3.Error) as e:
                f.write(f" Could not read browser history: {e}\n")

    write_csv_report(csv_filename, history_rows, ["browser", "url", "title", "visit_count", "last_visit_time"])
    print(f"[+] Browser History saved to {filename}")
    return history_rows


def get_platform_artifact_paths():
    # Artifacts are files or folders that may be useful during investigation.
    system_name = platform.system()
    home_dir = os.path.expanduser("~")
    possible_paths = []

    if system_name == "Windows":
        possible_paths = [
            os.path.join(home_dir, "AppData", "Roaming", "Microsoft", "Windows", "Recent"),
            os.path.join(home_dir, "AppData", "Local", "Temp"),
            "C:\\Windows\\Prefetch",
            "C:\\Windows\\System32\\winevt\\Logs"
        ]
    elif system_name == "Darwin":
        possible_paths = [
            os.path.join(home_dir, ".zsh_history"),
            os.path.join(home_dir, ".bash_history"),
            os.path.join(home_dir, "Library", "Logs"),
            "/var/log",
            "/Library/LaunchAgents",
            "/Library/LaunchDaemons"
        ]
    else:
        possible_paths = [
            os.path.join(home_dir, ".bash_history"),
            os.path.join(home_dir, ".zsh_history"),
            os.path.join(home_dir, ".local", "share", "recently-used.xbel"),
            "/etc/os-release",
            "/var/log",
            "/etc/systemd/system",
            "/etc/cron.d"
        ]

    artifacts = []
    for path in possible_paths:
        if os.path.exists(path):
            artifact_type = "Directory" if os.path.isdir(path) else "File"
            artifacts.append({
                "platform": system_name,
                "path": path,
                "type": artifact_type
            })

    return artifacts


def get_platform_artifacts():
    print("[*] Collecting Platform Artifacts...")
    filename = f"{OUTPUT_DIR}/platform_artifacts_{TIMESTAMP}.txt"
    csv_filename = f"{OUTPUT_DIR}/platform_artifacts_{TIMESTAMP}.csv"
    artifacts = get_platform_artifact_paths()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Platform Artifacts - {TIMESTAMP}\n")
        f.write("="*60 + "\n")
        if not artifacts:
            f.write("No common platform artifacts found.\n")
        for artifact in artifacts:
            f.write(f"{artifact['type']}: {artifact['path']}\n")

    write_csv_report(csv_filename, artifacts, ["platform", "path", "type"])
    print(f"[+] Platform Artifacts saved to {filename}")
    return artifacts


def run_triage():
    create_report_structure()
    summary = {
        "system_info": get_system_info(),
        "network_connections": get_network_connections(),
        "running_processes": get_running_processes(),
        "startup_programs": get_startup_programs(),
        "recent_temp_files": get_temp_files(),
        "browser_history": get_browser_history(),
        "platform_artifacts": get_platform_artifacts()
    }
    summary_filename = f"{OUTPUT_DIR}/triage_summary_{TIMESTAMP}.json"
    write_json_summary(summary_filename, summary)
    print(f"[+] JSON Summary saved to {summary_filename}")
    print("[+] Triage Complete.")
    return summary






if __name__ == "__main__":
    run_triage()

