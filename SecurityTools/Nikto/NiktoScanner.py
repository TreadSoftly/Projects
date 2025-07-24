#!/usr/bin/env python3

import os
import re
import argparse
import subprocess
from datetime import datetime

def usage():
    """
    Print the help message and exit the script.
    """
    print("Usage: script.py [options] <target>")
    print("Options:")
    print("  -p, --port <port>         Specify the port (default: 80)")
    print("  -h, --help                Display this help message")
    print("Example:")
    print("  script.py -p 8080 example.com")
    exit(1)

def identify_target_type(input_str):
    """
    Identify the type of the target (IP, domain, port, mac, url, asn) using regular expressions.

    :param input_str: The input string to identify
    :return: The identified target type or "unknown" if not matched
    """
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

def run_tool(tool, command, output_file):
    """
    Run a specified tool if it is installed and save the output to a file.

    :param tool: The name of the tool
    :param command: The command to run
    :param output_file: The file to save the output
    """
    if subprocess.getoutput(f"command -v {tool}") != '':
        with open(output_file, 'w') as file:
            subprocess.run(command, shell=True, stdout=file)
    else:
        print(f"{tool} is not installed. Skipping {tool}.")

def main(target, port):
    """
    Main function to run the Nikto scan.

    :param target: The target to scan
    :param port: The port to scan
    """
    # Check if the target is reachable
    if subprocess.run(['ping', '-c', '1', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        print(f"{target} is not reachable")
        exit(1)

    # Create output folder
    out_folder = f"{os.getenv('HOME')}/Desktop/LEVERAGE_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(f"{out_folder}/nikto", exist_ok=True)

    # Run Nikto scan
    run_tool("nikto", f'nikto -host {target} -port {port} -o "{out_folder}/nikto/nikto_output.txt"', f"{out_folder}/nikto/nikto_output.txt")

    print(f"Nikto scan results are located at {out_folder}/nikto/nikto_output.txt")

# Argument parser
parser = argparse.ArgumentParser(description="Nikto Scanning Script", add_help=False)
parser.add_argument("target", nargs='?', help="The target domain or IP address.")
parser.add_argument("-p", "--port", default="80", help="Specify the port (default: 80)")
parser.add_argument("-h", "--help", action="store_true", help="Display this help message")
args = parser.parse_args()

# Validate arguments and run the main function
if args.help or args.target is None:
    usage()

# Identify the target type
target_type = identify_target_type(args.target)
print(f"Identified target type: {target_type}")

# Run the main function
main(args.target, args.port)


# Explanation:
# Argument Parsing: The script uses Python's argparse library to handle command-line arguments, allowing the user to specify the target and port.
# Target Identification: The identify_target_type function uses regular expressions to match the input string to various patterns representing IP addresses, domains, ports, MAC addresses, URLs, and ASNs.
# Running Nikto: The main function performs a Nikto scan on the specified target and port. It first checks if the target is reachable, then creates an output directory, and finally runs the Nikto command using the run_tool function, writing the results to an output file.
# Help and Usage Information: The usage function prints a help message and exits the script if the user requests help or provides incorrect command-line arguments.
# Error Handling: The script includes checks for potential issues such as missing command-line arguments, unreachable targets, and missing dependencies like Nikto.
# Output Handling: Results are saved to a specified output directory under the user's Desktop.
