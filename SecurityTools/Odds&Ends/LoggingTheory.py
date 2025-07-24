#!/usr/bin/env python3

import os
import subprocess
import argparse
from datetime import datetime
import shutil
import getpass

# Global variables
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log.sh.log")
LOG_COLORS = {
    "DEBUG": "\033[0;34m",
    "INFO": "\033[0;32m",
    "WARN": "\033[1;33m",
    "ERROR": "\033[0;31m",
    "FATAL": "\033[0;31m",
    "NC": "\033[0m"
}

def log(log_priority, log_message):
    """
    Log messages to both console and file.

    :param log_priority: Priority level of log (DEBUG, INFO, WARN, ERROR, FATAL)
    :param log_message: The message to log
    """
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = LOG_COLORS.get(log_priority, LOG_COLORS["NC"])
    
    # Log to console
    console_message = f"{color}{date_time} [{log_priority}] {log_message}{LOG_COLORS['NC']}"
    print(console_message)

    # Log to file
    with open(LOG_FILE, 'a') as file:
        file.write(f"{date_time} [{log_priority}] {log_message}\n")

    # Exit if fatal error
    if log_priority == "FATAL":
        exit(1)

def secure_memory_allocation():
    """
    Securely allocate memory using tmpfs.
    """
    os.makedirs("/secure_memory", exist_ok=True)
    subprocess.run(["mount", "-t", "tmpfs", "-o", "size=512M", "tmpfs", "/secure_memory"])

def memory_zeroization(target_file):
    """
    Zeroize the given target file.

    :param target_file: Path to the target file
    """
    file_size = os.path.getsize(target_file)
    with open(target_file, 'wb') as file:
        file.write(b'\0' * file_size)
    os.remove(target_file)

def memory_analysis_prevention():
    """
    Apply techniques to prevent memory analysis.
    """
    log("Starting memory analysis prevention techniques...", "INFO")
    with open("/proc/sys/kernel/core_pattern", 'w') as file:
        file.write("0\n")
    secure_memory_allocation()
    log("Memory analysis prevention techniques completed.", "INFO")

def anti_forensics():
    """
    Apply anti-forensics techniques to make forensic analysis more challenging.
    """
    log("Starting anti-forensics techniques...", "INFO")

    # Securely remove temporary files
    subprocess.run(["srm", "-vz", "/tmp/zerofile"])
    subprocess.run(["cat", "/dev/null", ">", "~/.bash_history"], shell=True)
    subprocess.run(["history", "-c", "&&", "history", "-w"], shell=True)
    subprocess.run(["rm", "-rf", "/tmp/*", "/var/tmp/*"], shell=True)
    subprocess.run(["find", "/var/cache", "-type", "f", "-exec", "srm", "-v", "{}", ";"], shell=True)
    subprocess.run(["find", "/", "-exec", "touch", "-t", "202301010000.00", "{}", ";"], shell=True)
    subprocess.run(["swapoff", "-a", "&&", "srm", "-v", "/swapfile", "&&", "swapon", "-a"], shell=True)
    subprocess.run(["find", "/var/log", "-type", "f", "-exec", "srm", "-v", "{}", ";"], shell=True)

    # Clear user bash histories
    for user in os.listdir("/home"):
        with open(f"/home/{user}/.bash_history", 'w'):
            pass

    subprocess.run(["rm", "-rf", "~/.cache/thumbnails/*"], shell=True)
    subprocess.run(["ifconfig", "eth0", "down"])
    subprocess.run(["macchanger", "-r", "eth0"])
    subprocess.run(["ifconfig", "eth0", "up"])
    hostname = subprocess.getoutput("head /dev/urandom | tr -dc a-z | head -c 8")
    subprocess.run(["hostname", hostname])

    with open("/proc/sys/kernel/core_pattern", 'w') as file:
        file.write("0\n")

    log("Anti-forensics techniques completed.", "INFO")

# Argument parser
parser = argparse.ArgumentParser(description="Security and Forensics Script", add_help=False)
parser.add_argument("--anti-forensics", action="store_true", help="Apply anti-forensics techniques.")
parser.add_argument("--memory-prevention", action="store_true", help="Apply memory analysis prevention techniques.")
args = parser.parse_args()

# Validate arguments and run the main function
if args.anti_forensics:
    anti_forensics()

if args.memory_prevention:
    memory_analysis_prevention()
