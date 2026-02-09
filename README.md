# FirstResponse: Automated Triage Collector

## Overview
FirstResponse is a lightweight Python-based incident response tool designed for first responders and IT technicians. It automates the collection of volatile system data (processes and network state) to aid in forensic analysis.

## Features
- **Volatile Data Preservation**: Captures running processes and active network connections before system shutdown.
- **Forensic Logging**: Outputs timestamped text files for chain-of-custody integrity.
- **Lightweight**: Uses `psutil` for minimal system impact during collection.

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the collector: `python main.py`
3. View reports in the `triage_reports/` directory.

## Requirements
- Python 3.7+
- Administrator/root privileges (recommended for complete data collection)

## Future Roadmap
- [ ] Add Hash calculation (MD5/SHA256) for running executables
- [ ] Implement browser history scraping
- [ ] Add support for Linux/macOS specific artifacts
- [ ] Export to JSON/CSV format for automated analysis

## Author
Just a cybersecurity student practicing in building python-based tools designed for IT and Cybersecurity. -hexidecinull