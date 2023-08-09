#!/usr/bin/env python3

import re
import os
import sys
import argparse
import subprocess
from datetime import datetime

def identify_target_type(input_str):
    # Patterns to identify the target type
    patterns = [
        ("ip", r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"),
        ("domain", r"^(?:[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$"),
        ("port", r"^\d{1,5}$"),
        ("mac", r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"),
        ("url", r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w._~:/?#[\]@!$&()*+,;=]*)?$"),
        ("asn", r"^AS\d+$")
    ]

    # Check the input string against each pattern and return the matched type
    for pattern_type, pattern_regex in patterns:
        if re.match(pattern_regex, input_str):
            return pattern_type

    return "unknown" # Return unknown if no pattern matches

def show_help():
    # Print the help message
    parser.print_help()

def run_masscan(target, port, rate, duration):
    # Create the output folder
    out_folder = f"{os.getenv('HOME')}/Desktop/MASSCAN_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(out_folder, exist_ok=True)

    # Check if the target is reachable
    if subprocess.run(['ping', '-c', '1', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        print(f"{target} is not reachable")
        exit(1)

    # Check if Masscan is installed
    if subprocess.getoutput("command -v masscan") == '':
        print("Masscan is not installed. Cloning masscan from GitHub and compiling...")
        masscan_path = "https://github.com/robertdavidgraham/masscan"
        subprocess.run(['git', 'clone', masscan_path])
        os.chdir('masscan')
        subprocess.run(['make'])
        subprocess.run(['sudo', 'make', 'install'])
        os.chdir('..')
        subprocess.run(['rm', '-rf', 'masscan'])

    # Construct the Masscan command
    masscan_command = f"masscan -p{port} --rate={rate} --wait=0 --duration={duration} --output-format txt --output-filename \"{out_folder}/masscan_output.txt\" \"{target}\""

    # Execute the Masscan command
    print("Running masscan with the following command:")
    print(masscan_command)
    subprocess.run(masscan_command, shell=True)

    print(f"Masscan results are located at {out_folder}/masscan_output.txt")

# Argument parser to handle command-line arguments
parser = argparse.ArgumentParser(description="Masscan Script")
parser.add_argument("target", help="The target domain or IP address.")
parser.add_argument("-p", "--port", default="0-65535", help="Set the port range to scan (default: 0-65535)")
parser.add_argument("-r", "--rate", default="1000", help="Set the packet rate for masscan (default: 1000)")
parser.add_argument("-d", "--duration", default="20m", help="Set the scan duration (default: 20m)")
args = parser.parse_args()

# Check for target
if args.target is None:
    show_help()
    exit(1)

# Identify the target type
target_type = identify_target_type(args.target)
if target_type == "unknown":
    print("Unknown target type. Please enter a valid IP, domain, port, MAC address, URL, or ASN.")
    exit(1)

# Run the masscan function with the provided arguments
# run_masscan(args.target, args.port, args.rate, args.duration)
# Explanations and Comments
# identify_target_type Function: This function takes an input string and identifies whether it's an IP address, domain, port, MAC address, URL, or ASN. It returns the type as a string.
# Regular Expressions: Regular expressions are used to match the input string against various patterns. The re module is used for this purpose.
# Pattern Matching: The function iterates through each pattern and returns the corresponding type if the pattern matches the input string.
# Integration with Existing Script: The function is called within the main script to identify the target type before running the masscan command.
# Error Handling for Unknown Target Type: If the target type is identified as "unknown," the script prints an error message and exits.
