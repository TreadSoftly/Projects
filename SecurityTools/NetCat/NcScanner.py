#!/usr/bin/env python3

import os
import re
import argparse
import subprocess
from datetime import datetime

def show_help(parser):
    # Print the help message
    parser.print_help()

def identify_target_type(input_str):
    # Define patterns to identify the target type
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

def nc_iSpy(target, port, out_folder):
    # Check if the target is reachable
    if subprocess.run(['ping', '-c', '1', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        print(f"{target} is not reachable")
        exit(1)

    # Create output directory
    os.makedirs(f"{out_folder}/nc", exist_ok=True)

    # Check if 'nc' is installed
    if subprocess.getoutput("command -v nc") == '':
        print("Netcat is not installed. Skipping nc.")
        return

    # Run nc command
    output_file = f"{out_folder}/nc/nc_scan.txt"
    nc_command = f"nc -v -z {target} {port} | grep -v 'Connection to' | sed 's/^[ \\t]*//;s/[ \\t]*$//'"
    with open(output_file, 'w') as file:
        subprocess.run(nc_command, shell=True, stdout=file, stderr=subprocess.DEVNULL)

    print(f"Netcat results are located at {output_file}")

# Argument parser
parser = argparse.ArgumentParser(description="Netcat Port Scanning Script")
parser.add_argument("target", help="The target domain or IP address.")
parser.add_argument("-p", "--port", default="0-65535", help="Specify the port range for the scan (default: 0-65535)")
parser.add_argument("-o", "--output", default=f"{os.getenv('HOME')}/Desktop/NC_SCAN_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}", help="Specify the output directory")
args = parser.parse_args()

# Validate arguments and run the function
if args.target is None:
    show_help(parser)
    exit(1)

# Identify the target type
target_type = identify_target_type(args.target)
print(f"Identified target type: {target_type}")

# Run the nc_iSpy function
nc_iSpy(args.target, args.port, args.output)

# Explanation:
# Argument Parsing: The script uses Python's argparse library to handle command-line arguments, allowing the user to specify the target, port range, and output directory.
# Target Identification: The identify_target_type function uses regular expressions to match the input string to various patterns representing IP addresses, domains, ports, MAC addresses, URLs, and ASNs.
# Netcat Port Scan: The nc_iSpy function performs a port scan using Netcat (nc) on the specified target and port range. It first checks if the target is reachable using the ping command, then checks if Netcat is installed, and finally runs the Netcat command, writing the results to an output file.
# Error Handling: The script includes checks for potential issues such as missing command-line arguments, unreachable targets, and missing dependencies like Netcat.
# Output Handling: Results are saved to a specified output directory, with a default location under the user's Desktop.
