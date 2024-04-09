#The file is called nmapscan.py

#Below you will have to set your own path to where the script is held in your directory: 
# LOOKE FOR AND EDIT> 
    # Output results to a file
    # report_filename = os.path.join("C:\\Users\\YOU\\SET\\YOU\\DIRECTORYPATH", f"nmapscan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")

#The vulnscan at the end is being built out and worked on currently

########################################################################################################################################################################
  #BELOW COMMENTED OUT IS WHERE THE VULNSCAN.PY SCRIPT WOULD TAKE THE JSON FILE FROM THE NMAPSCAN.PY SCAN AND WORK ON THE FINDINGS USING NVD API URL TO DIG FURTHER
  #WILL FINISH CREATING AND TESTING THIS BUT FOR NOW IF YOU CREATE A VULNSCAN.PY SCRIPT THIS WILL WORK WITH THAT AND TAKE IN THE JSON FILE THAT THE NMAPSCAN.PY CREATES
  #FOR NOW IT WILL BE COMMENTED OUT BUT THE NMAPSCAN.PY WORKS FINE AS A STANDALONE
########################################################################################################################################################################

import nmap  # Importing the nmap library for network scanning
import concurrent.futures  # Importing the concurrent.futures module for parallel execution
import os  # Importing the os module for interacting with the operating system
import socket  # Importing the socket module for network communication
import sys  # Importing the sys module for system-specific parameters and functions
import multiprocessing  # Importing the multiprocessing module for utilizing multiple CPU cores
import contextlib  # Importing the contextlib module for context management utilities
from tqdm import tqdm  # Importing the tqdm library for creating progress bars
import time  # Importing the time module for time-related functions
from typing import Dict, List, Tuple, Union, Optional  # Importing type hints for function signatures
import copy  # Importing the copy module for creating deep copies of objects
from colorama import Fore, Style, init  # Importing the colorama library for colored terminal output
init(autoreset=True) # Initializing colorama for auto-resetting colors after each print statement
import json # Importing the json module for serialization and deserialization of objects and functions from JSON files
import subprocess # Importing the subprocess module for serialization and deserialization of objects and functions from JSON files
import progressbar # Importing the progressbar module for serialization and deserialization

# Ensure Nmap is available
try: # Using a try block to handle exceptions in Python exceptions that are not caught by the standard exception handler module
    nm = nmap.PortScanner()  # Creating an instance of the PortScanner class from the nmap library
except nmap.PortScannerError as e: # Handling the exception if an error occurs while creating the PortScanner instance
    print(f"{Fore.RED}{Style.BRIGHT}Nmap not found: {e}{Style.RESET_ALL}")  # Printing an error message if Nmap is not found on the system or an error occurs while creating the PortScanner instance
    sys.exit(1)  # Exiting the program with a non-zero exit code if Nmap is not found or an error occurs while creating the PortScanner instance
except Exception as e: # Handling any other exceptions that may occur while creating the PortScanner instance or running the network scan
    print(f"{Fore.RED}{Style.BRIGHT}Unexpected error: {e}{Style.RESET_ALL}")  # Printing an unexpected error message if Unexpected error occurs while creating the PortScanner instance or running the network scan
    sys.exit(1)  # Exiting the program with a non-zero exit code if an unexpected error occurs while creating the PortScanner instance or running the network scan

@contextlib.contextmanager # Using the contextlib module to create a context manager for suppressing stdout and stderr output temporarily
def suppress_stdout_stderr(): # Defining a function to suppress stdout and stderr output temporarily
    with open(os.devnull, 'w') as fnull: # Opening the null device for writing to suppress the output
        old_stdout, old_stderr = sys.stdout, sys.stderr # Saving the original stdout and stderr streams
        sys.stdout, sys.stderr = fnull, fnull # Redirecting stdout and stderr to the null device to suppress the output
        try: # Using a try block to handle exceptions
            yield # Yielding to the context manager to execute the code within the context
        finally: # Using a finally block to ensure cleanup
            sys.stdout, sys.stderr = old_stdout, old_stderr # Restoring the original stdout and stderr streams

CPU_CORES = multiprocessing.cpu_count() or 1  # Getting the number of CPU cores or defaulting to 1 if not available

def get_local_ip() -> str: # Defining a function to get the local IP address of the current process and return it as a string in the format expected by the current process and previous process manager
    try: # Using a try block to handle exceptions
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: # Creating a socket object for network communication
            s.connect(('10.255.255.255', 1))  # Connecting to a dummy IP address to get the local IP
            local_ip = s.getsockname()[0]  # Getting the local IP address
    except Exception: # Handling exceptions that may occur while getting the local IP address
        local_ip = '127.0.0.1'  # Defaulting to localhost IP if an error occurs
    return local_ip # Returning the local IP address as a string

def quick_scan(ip: str, nm: nmap.PortScanner) -> Dict[str, List[int]]: # Checking if scan information is available and returning the detailed scan results if available otherwise returning None
    print(f"{Fore.YELLOW}{Style.BRIGHT}Performing Initial Scan For {Fore.RED}{Style.BRIGHT}Open Ports:{Style.RESET_ALL}") # Checking for open ports in the specified IP address range and printing a message to indicate the start of the scan
    arguments = "-T4 --open" # Setting the Nmap scan arguments for quick scanning on TCP and UDP ports with open ports
    nm.scan(hosts=ip, ports="1-65535", arguments=arguments) # Checking for open ports in the specified IP address range
    open_ports: Dict[str, List[int]] = {'tcp':[],'udp':[]} # List of open ports for each protocol
    for proto in nm[ip].all_protocols(): # Iterating over the protocols to check for open ports
        ports = sorted(nm[ip][proto].keys())
        bar = progressbar.ProgressBar(max_value=len(ports)) # Creating a progress bar to track the scanning progress
        for i, port in enumerate(ports): # Iterating over the ports to check if they are open
            if nm[ip][proto][port]['state'] == 'open': # Checking if the port is open
                open_ports[proto].append(port) # Adding the open port to the open_ports dictionary
            bar.update(i) # type: ignore
        bar.finish()
    return open_ports # Returning the open ports as a dictionary

def scan_port(ip: str, port: int, proto: str, nm: nmap.PortScanner) -> Tuple[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]: # Defining a function to scan a specific port on the specified IP address and return detailed information about the port
    arguments = "-T4 -sV -sC -A -O --version-intensity 9 --script=banner,vuln"  # Setting the Nmap scan arguments for detailed scanning
    nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)  # Scanning the specified port for detailed information
    scan_info = nm[ip].get(proto, {}).get(port, {})  # Getting the scan information for the port
    result = { # Creating a dictionary to store the detailed scan results
        "state": scan_info.get('state', 'closed'),  # Getting the state of the port (open or closed)
        "name": scan_info.get('name', ''),  # Getting the name of the service running on the port
        "product": scan_info.get('product', ''),  # Getting the product information of the service
        "version": scan_info.get('version', ''),  # Getting the version information of the service
        "extrainfo": scan_info.get('extrainfo', ''),  # Getting additional information about the service
        "reason": scan_info.get('reason', ''),  # Getting the reason for the port state
        "script": scan_info.get('script', {})  # Getting the script output for the port
    } if scan_info else None  # Checking if scan information is available and returning the detailed scan results if available
    return port, result # Returning the port number and detailed scan results as a tuple

def worker(ip: str, ports: List[int], proto: str, nm: nmap.PortScanner) -> Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]: # Checking if scan information is available and returning the detailed scan results if available
    results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = {} # Dictionary of ports and ports that are available for the worker to scan
    for port in ports: # Iterating over the ports to scan
        port_result = scan_port(ip, port, proto, nm) # Checking if scan information is available and returning the detailed scan results if available
        if port_result[1]: # Checking if the detailed scan results are available
            results[port_result[0]] = port_result[1] # The port number and detailed scan results are stored in the results dictionary
    return results # Returning the port number and detailed scan results as a dictionary

def distribute_work(ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]: # Defining a function to distribute the detailed scanning work across multiple threads for parallel execution
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}
    proto = None # Initializing the protocol to None
    with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_CORES) as executor: # Using a ThreadPoolExecutor to distribute the work across multiple threads for parallel execution
        futures: List[concurrent.futures.Future[Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]]] = []
        for proto, ports in open_ports.items(): # Iterating over the open ports for each protocol
            if ports: # Checking if there are open ports for the protocol
                print(f"{Fore.BLUE}{Style.BRIGHT}Performing Detailed Scan On Open Ports:{Style.RESET_ALL}") # Printing a message to indicate the start of the detailed scanning process
                for port in ports: # Iterating over the open ports for detailed scanning
                    nm_copy = copy.deepcopy(nm) # Creating a deep copy of the nmap.PortScanner object to avoid
                    futures.append(executor.submit(worker, ip, [port], proto, nm_copy)) # Submitting the worker task to the executor
        pbar = tqdm(total=len(futures), # Creating a progress bar to track the detailed scanning progress
                desc=f"{Fore.RED}{Style.BRIGHT}Detailed Scanning Progress{Fore.GREEN}{Style.BRIGHT}:Initializing:{Style.RESET_ALL}", # Setting the description of the progress bar to indicate the detailed scanning progress
                unit="port", # Setting the unit of the progress bar to 'port'
                leave=False, # Leave the progress bar after completion
                bar_format="{l_bar}\033[95m{bar}\033[0m{r_bar}[Remaining:{remaining}][Elapsed:{elapsed}]{rate_fmt}/[{n_fmt}|{total_fmt}]") # Creating a progress bar to track the detailed scanning progress
        for future in concurrent.futures.as_completed(futures): # Iterating over the completed futures
            proto_results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = future.result() # Getting the results of the future task
            for port, result in proto_results.items():
                if proto is not None and result is not None: # Checking if the protocol and result are not None
                    detailed_results[proto][port] = result
                    pbar.set_description(f"{Fore.GREEN}{Style.BRIGHT}Scanning Port: {Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}") # Setting the description of the progress bar to indicate the port being scanned
                    pbar.update() # update the progress bar
        pbar.close() # Closing the progress bar

    # Print the detailed scan results
    for proto, ports_info in detailed_results.items(): # Iterating over the detailed scan results for each protocol
        for port, info in ports_info.items(): # Iterating over the port information for the protocol
            print(f"Port {port}:")  # Printing the port number
            print(f"  State: {info.get('state')}")  # Printing the state of the port
            print(f"  Name: {info.get('name')}")  # Printing the name of the service running on the port
            print(f"  Product: {info.get('product')}")  # Printing the product information of the service
            print(f"  Version: {info.get('version')}")  # Printing the version information of the service
            print(f"  Extra Info: {info.get('extrainfo')}")  # Printing additional information about the service
            print(f"  Reason: {info.get('reason')}")  # Printing the reason for the port state
            print(f"  Script Output:")  # Printing the script output for the port
            script_info = info.get('script') # The script output for the port state machine
            if isinstance(script_info, dict): # Checking if the script output is a dictionary
                for key, value in script_info.items(): # Iterating over the script output
                    if 'vuln' in key.lower() or 'cve' in key.lower(): # Checking if the key contains 'vuln' or 'cve'
                        print(f"    {Fore.RED}{Style.BRIGHT}{key}: {value}{Style.RESET_ALL}")  # Printing the script output with highlighting for vulnerabilities or CVEs
                print() # Printing a new line after the script output
            else: # Handling the case where the script output is not a dictionary
                print(f"    No script output\n")  # Printing a message if there is no script output
    return detailed_results # Returning the detailed scan results as a dictionary

def main(): # Defining the main function to orchestrate the network scanning process
    ip = get_local_ip()  # Getting the local IP address
    print(f"{Fore.RED}{Style.BRIGHT}Scanning {Fore.GREEN}{Style.BRIGHT}{ip} {Fore.RED}{Style.BRIGHT}Using Optimal System Resources{Style.RESET_ALL}")  # Printing a message indicating the start of the scan
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}  # Initializing a dictionary to store the open ports
    distribute_work(ip, open_ports)  # Performing the distributed work to update the open_ports dictionary

    # Quick Scan
    open_ports = quick_scan(ip, nm)  # Performing the quick scan and getting the open ports
    print(f"{Fore.GREEN}{Style.BRIGHT}Quick Scan Completed. Identified Open Ports: {Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['tcp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}(TCP),{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['udp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}(UDP){Style.RESET_ALL}")  # Printing the identified open ports

    # Detailed Scan on Open Ports
    detailed_results = {} # Initializing a dictionary to store the detailed scan results in a dictionary object containing the details of the open ports discovered in the database
    if open_ports: # Initializing a dictionary to store the detailed scan results in a dictionary object containing the details of the open ports discovered in the database
        detailed_results = distribute_work(ip, open_ports)  # Performing the distributed work on the identified open ports

    # Output results to a file
    report_filename = os.path.join("C:\\Users\\YOU\\SET\\YOU\\DIRECTORYPATH", f"nmapscan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")  # Generating the report filename with the current timestamp
    with open(report_filename, "w") as report_file: # Opening the report file in write mode
        for proto, ports_info in detailed_results.items(): # Iterating over the detailed scan results for each protocol
            report_file.write(f"{proto.upper()} Ports:{Style.RESET_ALL}\n")  # Writing the protocol name to the report file
            for port, info in ports_info.items(): # Iterating over the port information for the protocol
                if info:  # Ensure there's information to write
                    state = info.get("state", "N/A")  # Getting the state of the port
                    service = info.get("name", "Unknown service")  # Getting the name of the service running on the port
                    product = info.get("product", "")  # Getting the product information of the service
                    version = info.get("version", "")  # Getting the version information of the service
                    extra = info.get("extrainfo", "")  # Getting additional information about the service
                    reason = info.get("reason", "")  # Getting the reason for the port state
                    script_info = info.get("script", {})  # Getting the script output for the port
                    if isinstance(script_info, dict): # Checking if the script output is a dictionary
                        script_output = "\n".join([f"{str(k)}: {str(v)}" if 'vuln' not in str(k).lower() and 'cve' not in str(k).lower() else f"{Fore.RED}{Style.BRIGHT}{str(k)}: {str(v)}{Style.RESET_ALL}" for k, v in script_info.items()])  # Formatting the script output
                    else: # Handling the case where the script output is not a dictionary
                        script_output = "" # Setting the script output to an empty string
                    report_line = f"Port {port}/TCP {state}: {service} {product} {version} {extra} {reason}\nScript Output:\n{script_output}\n\n"  # Generating the report line
                    if 'vuln' in script_output.lower() or 'cve' in script_output.lower(): # Checking if vulnerabilities or CVEs are detected in the script output
                        report_file.write(f"WARNING: Vulnerabilities or CVEs detected!{Style.RESET_ALL}\n")  # Writing a warning message to the report file if vulnerabilities or CVEs are detected
                    report_file.write(report_line)  # Writing the report line to the report file
    print(f"{Fore.BLUE}{Style.BRIGHT}Detailed report saved to {report_filename}{Style.RESET_ALL}")  # Printing the filename of the saved report

    # Save scan results in JSON format for the vulnerability scanning script
    results_json_path = os.path.join("C:\\Users\\MrDra\\OneDrive\\Desktop\\PythonTools", f"nmapscan_results_{time.strftime('%Y%m%d%H%M%S')}.json") # Generating the JSON file path for the vulnerability scanning script
    with open(results_json_path, 'w') as json_file: # Opening the JSON file in write mode
        json.dump(detailed_results, json_file, indent=4) # Writing the detailed scan results to the JSON file with indentation
    print(f"{Fore.YELLOW}{Style.BRIGHT}Detailed report saved to {results_json_path}{Style.RESET_ALL}") # Printing the filename of the saved JSON file for the vulnerability scanning script with indentation and indent level of 4


########################################################################################################################################################################
  #THIS IS WHERE THE VULNSCAN.PY SCRIPT WOULD TAKE THE JSON FILE FROM THE NMAPSCAN.PY SCAN AND WORK ON THE FINDINGS USING NVD API URL TO DIG FURTHER
  #WILL FINISH CREATING AND TESTING THIS BUT FOR NOW IF YOU CREATE A VULNSCAN.PY SCRIPT THIS WILL WORK WITH THAT AND TAKE IN THE JSON FILE THAT THE NMAPSCAN.PY CREATES
  #FOR NOW IT WILL BE COMMENTED OUT BUT THE NMAPSCAN.PY WORKS FINE AS A STANDALONE
########################################################################################################################################################################

  
#    # Prompt user to initiate vulnerability scanning
#    user_input = input("Do you want to proceed with vulnerability scan? (y/n): ") # Prompting the user to initiate the vulnerability scan with y/n parameter values (y/n):
#    if user_input.lower() == 'y' or user_input.upper() == 'Y': # Checking if the user input is 'y' or 'Y'
#        print("Proceeding with vulnerability scan...") # Prompting the user to proceed with the vulnerability scan
#        # Assuming `results_json_path` holds the path to the JSON file from nmap scan
#        vulnscan_script_path = os.path.join(os.path.dirname(__file__), "vulnscan.py") # Path to the vulnerability scanning script file
#        output_dir = os.path.join(os.path.dirname(vulnscan_script_path), "vulnscan_results") # Directory to store the vulnerability scanning results file

#        # Create the output directory if it doesn't exist
#        os.makedirs(output_dir, exist_ok=True)

#        # Execute vulnscan.py script with real-time output
#        try: # Running vulnscan.py script with real-time output
#            command = ["python", vulnscan_script_path, results_json_path, output_dir] # Creating a command to execute the vulnerability scanning script with the JSON file path and output directory
#            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process: # Using the subprocess module to execute the vulnerability scanning script with real-time output instead of using the os.system() function
#                while process.stdout is not None: # Checking if the output directory is not empty before reading the line from the output directory
#                    line = process.stdout.readline() # Read the line from the output directory and convert it to a string
#                    if not line: # Checking if the line is empty is not necessary as the loop will
#                        break # Ignore error and continue processing further lines from the output directory
#                    print(line, end='') # print line from the output directory if it exists and is not empty
#            process.wait()  # Wait for the process to complete

#            if process.returncode != 0: # Something went wrong during the execution of the vulnerability scanning script
#                print(f"{Fore.RED}{Style.BRIGHT}Vulnerability scan encountered an error.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script with real-time output
#        except Exception as e: # pylint: disable=broad-except instead of returning an exception
#            print(f"{Fore.RED}{Style.BRIGHT}Failed to execute vulnscan.py: {e}{Style.RESET_ALL}") # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan

#        # Assuming `results_json_path` holds the path to the JSON file from nmap scan
#        vulnscan_script_path = os.path.join(os.path.dirname(__file__), "vulnscan.py") # Path to the vulnerability scanning script file
#        output_dir = os.path.join(os.path.dirname(vulnscan_script_path), "vulnscan_results") # Directory to store the vulnerability scanning results file

#        # Create the output directory if it doesn't exist
#        os.makedirs(output_dir, exist_ok=True) # Make sure output directory exists before running the vulnerability scanning script

#        # Execute vulnscan.py script with real-time output
#        try: # Using a try block to handle exceptions that may occur while executing the vulnerability scanning script
#            command = ["python", vulnscan_script_path, results_json_path, output_dir] # Creating a command to execute the vulnerability scanning script with the JSON file path and output directory
#            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process: # Using the subprocess module to execute the vulnerability scanning script with real-time output instead of using the os.system() function
#                while process.stdout is not None: # Checking if the output directory is not empty before reading the line from the output directory
#                    line = process.stdout.readline() # Read the line from the output directory and convert it to a string
#                    if not line: # Checking if the line is empty is not necessary as the loop will break if the line is empty
#                        break # Ignore error and continue processing further lines from the output directory
#                    print(line, end='') # print line from the output directory if it exists and is not empty
#            process.wait()  # Wait for the process to complete

#            if process.returncode != 0: # Checking if the process return code is not 0 means that the process encountered an error
#                print(f"{Fore.RED}Vulnerability scan encountered an error.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script
#        except Exception as e: # Handling exceptions that may occur while executing the vulnerability scanning script
#            print(f"{Fore.RED}Failed to execute vulnscan.py: {e}{Style.RESET_ALL}") # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
#    else: # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
#        print("Vulnerability scan aborted.") # Printing a message if the user chooses not to proceed with the vulnerability scan

    # Timing and final message
    elapsed_time = time.time() - start_time # Time difference between start_time and end_time for the last scan in seconds since the last time the script was run
    print(f"\n{Fore.GREEN}Total process completed in {elapsed_time:.2f} seconds.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script

if __name__ == "__main__": # Run the script if it is executed directly
    start_time = time.time()  # Record start time of the script
    main() # Run the script and wait for the script to complete before continuing with the script execution
