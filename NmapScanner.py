#!/usr/bin/env python3

import os
import subprocess
import argparse
from datetime import datetime

def nmap_iSpy(target, scan_type="tcp,udp", port="0-65535", verbosity=2, scan_duration="20m", scan_detail=3):
    """
    Run an Nmap scan on the specified target.

    :param target: The target to scan
    :param scan_type: The type of scan (default: "tcp,udp")
    :param port: The port range to scan (default: "0-65535")
    :param verbosity: The verbosity level of the scan (default: 2)
    :param scan_duration: The duration of the scan (default: "20m")
    :param scan_detail: The detail level of the scan (default: 3)
    """

    # Check if the target is reachable
    if subprocess.run(['ping', '-c', '1', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        print(f"{target} is not reachable")
        exit(1)

    # Create output folder
    out_folder = f"home/treadsoftly/Desktop/LEVERAGE_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(f"{out_folder}/nmap", exist_ok=True)

    # Define Nmap command
    nmap_command = f'nmap -O -sV --script=vulners -p {port} -v {verbosity} -T{scan_detail} --reason -sS -sU -sC -oX "{out_folder}/nmap/nmap_os_scan_{scan_type}.xml" -oN "{out_folder}/nmap/nmap_os_scan_{scan_type}.txt" -oG "{out_folder}/nmap/nmap_os_scan_{scan_type}.gnmap" --webxml --min-parallelism=14 {target}'

    # Run Nmap command
    with open(f"{out_folder}/nmap/nmap_os_scan_{scan_type}.log", 'w') as file:
        subprocess.run(nmap_command, shell=True, stdout=file)

    # Compress results with gzip, bzip2, and xz if available
    compress_commands = [
        ('gzip', '-9'),
        ('bzip2', '-9'),
        ('xz', '-9')
    ]
    for tool, option in compress_commands:
        if subprocess.getoutput(f"command -v {tool}") != '':
            for ext in ['xml', 'txt', 'gnmap']:
                subprocess.run(f'{tool} {option} "{out_folder}/nmap/nmap_os_scan_{scan_type}.{ext}"', shell=True)

    print(f"Nmap OS scan results are located at {out_folder}/nmap/nmap_os_scan_{scan_type}.*")

# Argument parser
parser = argparse.ArgumentParser(description="Nmap Scanning Script", add_help=False)
parser.add_argument("target", nargs='?', help="The target domain or IP address.")
args = parser.parse_args()

# Validate arguments and run the main function
if args.target is None:
    print("Error: target not specified")
    exit(1)

# Run the Nmap scan
nmap_iSpy(args.target)

# Explanation:
# Running Nmap Scan: The nmap_iSpy function is the main function responsible for performing the Nmap scan on the specified target with various options.
# Compressing Results: After the scan, the results are compressed using gzip, bzip2, and xz compression methods if available on the system.
# Checking Target Availability: Before running the scan, the script checks if the target is reachable using a simple ping command.
# Creating Output Directory: The script creates an output directory where all the scan results and logs are stored.
# Command-line Arguments: The target is specified as a command-line argument, and additional parameters can be modified within the function if needed.
# Logging: The script logs the standard output of the Nmap command to a log file.
