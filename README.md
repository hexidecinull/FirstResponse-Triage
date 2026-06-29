# FirstResponse: Simple Automated Triage Collector

## Overview
FirstResponse is a lightweight Python-based incident response tool designed for first responders and IT technicians. It automates the collection of volatile system data (processes and network state) to aid in forensic analysis.

## Features
- **Volatile Data Preservation**: Captures running processes and active network connections before system shutdown.
- **Forensic Logging**: Outputs timestamped text files for chain-of-custody integrity.
- **Lightweight**: Uses `psutil` for minimal system impact during collection.
- **Executable Hashing**: Calculates MD5 and SHA256 hashes for running process executables when accessible.
- **Browser History Collection**: Attempts to collect recent Chrome, Edge, and Firefox history from local    browser databases.
- **Platform Artifacts**: Lists common Windows, Linux, and macOS artifact locations when they exist.
- **Structured Exports**: Saves text reports, CSV files, and a JSON summary for easier analysis.

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the collector: `python main.py`
3. View reports in the `triage_reports/` directory.

## GUI Usage
1. Start the GUI from Command Prompt: `python gui.py`
2. Or start the GUI from PowerShell: `python .\gui.py`
3. Click *Run Full Triage* to collect reports.
4. Click *Open Reports Folder* to view saved reports.

## Requirements
- Python 3.7+
- Administrator/root privileges (recommended for complete data collection)

## Terminal Notes
- *Command Prompt*, *PowerShell*, and other shells can run this project as long as Python is installed.
- Run as Administrator/root when possible for more complete process and network data.
- Some browser history files may be locked or missing depending on which browsers are installed.

## NEW Updates!

- **GUI Usage** [WIP]
- **Hash Calculations** (MD5/SHA256)
- **Browser History Scrapping**
- **Additional support for Linux/ MacOs** [UNTESTED!] 
- **Export to JSON/CSV Format**

## Author
Just a cybersecurity student practicing in building python-based tools designed for IT and Cybersecurity. -hexidecinull
