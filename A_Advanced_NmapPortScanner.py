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
import time  # Importing the time module for time-related functions
from typing import Dict, List, Tuple, Union, Optional  # Importing type hints for function signatures
import copy  # Importing the copy module for creating deep copies of objects
from colorama import Fore, Style, init  # Importing the colorama library for colored terminal output
init(autoreset=True) # Initializing colorama for auto-resetting colors after each print statement
import json # Importing the json module for serialization and deserialization of objects and functions from JSON files
import subprocess # Importing the subprocess module for serialization and deserialization of objects and functions from JSON files
# import progressbar # Importing the progressbar module for serialization and deserialization
from halo import Halo  # type: ignore
from multiprocessing import cpu_count, Pool
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            sys.stdout, sys.stderr = old_stdout, old_stderr # Restoring the original stdout and stderr streamswith ThreadPoolExecutor(max_workers=cpu_count() or 1) as executor:

CPU_CORES = multiprocessing.cpu_count() or 1  # Getting the number of CPU cores or defaulting to 1 if not available

def get_local_ip() -> str: # Defining a function to get the local IP address of the current process and return it as a string in the format expected by the current process and previous process manager
    try: # Using a try block to handle exceptions
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: # Creating a socket object for network communication
            s.connect(('10.255.255.255', 1))  # Connecting to a dummy IP address to get the local IP
            local_ip = s.getsockname()[0]  # Getting the local IP address
    except Exception: # Handling exceptions that may occur while getting the local IP address
        local_ip = '127.0.0.1'  # Defaulting to localhost IP if an error occurs
    return local_ip # Returning the local IP address as a string

def scan_port(ip: str, port: int, proto: str, nm: nmap.PortScanner) -> Tuple[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    arguments = "-T4 -sV -sC -A -O -vv --version-intensity 9 --script=default,vuln,banner,http-headers,http-title"
    nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)
    scan_info = nm[ip].get(proto, {}).get(port, {})
    result = {
        "state": scan_info.get('state', 'closed'),
        "name": scan_info.get('name', ''),
        "product": scan_info.get('product', ''),
        "version": scan_info.get('version', ''),
        "extrainfo": scan_info.get('extrainfo', ''),
        "reason": scan_info.get('reason', ''),
        "osclass": scan_info.get('osclass', ''),
        "osmatch": scan_info.get('osmatch', ''),
        "osfamily": scan_info.get('osfamily', ''),
        "script": scan_info.get('script', {})
    } if scan_info else None
    return port, result

def quick_scan(ip: str, nm: nmap.PortScanner) -> Dict[str, List[int]]:
    print(f"{Fore.YELLOW}{Style.BRIGHT}Setting Up Initial Scan On {Fore.RED}{Style.BRIGHT}{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}SYSTEM{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")
    arguments = "-T3 --open"
    nm.scan(hosts=ip, ports="1-65535", arguments=arguments)
    open_ports: Dict[str, List[int]] = {'tcp':[],'udp':[]}
    spinner = Halo(text='Scanning ports', spinner='dots')
    spinner.start() # type: ignore
    for proto in nm[ip].all_protocols():
        ports = sorted(nm[ip][proto].keys())
        total_ports = len(ports)
        completed = 0
        with ThreadPoolExecutor(max_workers=cpu_count() or 1) as executor:
            futures = {executor.submit(nm[ip][proto].get, port): port for port in ports}
            for future in futures:
                port = future
                spinner.text = f'{Fore.GREEN}{Style.BRIGHT}Scan Submitted For{Style.RESET_ALL} [{Fore.BLUE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}]'
            for future in as_completed(futures):
                port = futures[future]
                if future.result()['state'] == 'open':
                    open_ports[proto].append(port)
                completed += 1
                percentage = (completed / total_ports) * 100
                spinner.text = f'Scanned {completed} of {total_ports} ports ({percentage:.2f}%)'
    spinner.stop()
    return open_ports

def scan_all_open_ports(ip: str):
    nm = nmap.PortScanner()
    open_ports = quick_scan(ip, nm)
    with Pool(processes=cpu_count() or 1) as pool:
        results: List[Tuple[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]] = pool.starmap(scan_port, [(ip, port, proto) for proto, ports in open_ports.items() for port in ports])
        for port, result in results:
            print(f"Port: {port}, Result: {result}")

def worker(ip: str, ports: List[int], proto: str, nm: nmap.PortScanner, spinner: Halo, completed: Dict[str, int]) -> Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = {}
    def scan_and_update(port: int, ip: str, proto: str, nm: nmap.PortScanner, spinner: Halo, completed: Dict[str, int], results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]):
        spinner.text = f'{Fore.YELLOW}{Style.BRIGHT}Initializing Scan On{Style.RESET_ALL} [{Fore.CYAN}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}]'
        port_result = scan_port(ip, port, proto, nm)
        percentage = 0
        if port_result[1]:
            results[port_result[0]] = port_result[1]
            completed['count'] += 1
            percentage = (completed['count'] / completed['total']) * 100
            spinner.text = f'{Fore.GREEN}{Style.BRIGHT}Finished Scan On {Style.RESET_ALL}[{Fore.BLUE}{Style.BRIGHT}Port:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}] [Completion:[{completed["count"]}/{completed["total"]}]{Fore.GREEN}{Style.BRIGHT} {percentage:.2f}%{Style.RESET_ALL}]'
            time.sleep(5)
        else:
            spinner.text = f'{Fore.RED}{Style.BRIGHT}No Results On{Style.RESET_ALL} [{Fore.GREEN}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}]'
        spinner.text = f'{Fore.GREEN}{Style.BRIGHT}Scan In Progress On{Style.RESET_ALL} [{Fore.BLUE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}] [Completion:[{completed["count"]}/{completed["total"]}]{Fore.GREEN}{Style.BRIGHT} {percentage:.2f}%{Style.RESET_ALL}]'
        time.sleep(15)
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(scan_and_update, ports, [ip]*len(ports), [proto]*len(ports), [nm]*len(ports), [spinner]*len(ports), [completed]*len(ports), [results]*len(ports))

    return results

def distribute_work(ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}
    proto = None
    total_ports = sum(len(ports) for ports in open_ports.values())
    completed = {'total': total_ports, 'count': 0}
    spinner = Halo(text=f'{Fore.GREEN}{Style.BRIGHT}Initializing', spinner='dots')  # Initialize spinner here
    with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_CORES) as executor:
        futures: List[concurrent.futures.Future[Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]]] = []
        for proto, ports in open_ports.items():
            if ports:
                print(f"{Fore.CYAN}{Style.BRIGHT}Performing Detailed Scan On {Fore.RED}{Style.BRIGHT}Open Ports:{Style.RESET_ALL}")
                spinner.start()  # type: ignore # Start spinner here
                for port in ports:
                    nm_copy = copy.deepcopy(nm)
                    futures.append(executor.submit(worker, ip, [port], proto, nm_copy, spinner, completed))
        for future in concurrent.futures.as_completed(futures):
            proto_results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = future.result()
            for port, result in proto_results.items():
                if proto is not None and result is not None:
                    detailed_results[proto][port] = result
        spinner.text = '{Fore.GREEN}{Style.BRIGHT}Finished Scanning All Ports{Style.RESET_ALL}'
        spinner.stop()

    def print_warning(message: str):
        if sys.stdout.isatty():
            print(f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}")
        else:
            print(f"WARNING: {message}")

    # Print the detailed scan results
    for proto, ports_info in detailed_results.items():
        for port, info in ports_info.items():
            print(f"{Fore.BLUE}{Style.BRIGHT}Port{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")
            print(f"  State: {info.get('state')}")
            print(f"  Name: {info.get('name')}")
            print(f"  Product: {info.get('product')}")
            print(f"  Version: {info.get('version')}")
            print(f"  Extra Info: {info.get('extrainfo')}")
            print(f"  Reason: {info.get('reason')}")
            print(f"  OS Class: {info.get('osclass')}")
            print(f"  OS Match: {info.get('osmatch')}")
            print(f"  OS Family: {info.get('osfamily')}")
            print(f"  Script Output:")
            script_info = info.get('script')
            if isinstance(script_info, dict):
                for key, value in script_info.items():
                    if 'vuln' in key.lower() or 'cve' in key.lower():
                        print_warning(f"{key}: {value}")
                    else:
                        print(f"{key}: {value}")
                print()
            else:
                print(f"No script output\n")
    return detailed_results

def main(): # Defining the main function to orchestrate the network scanning process
    ip = get_local_ip()  # Getting the local IP address
    print(f"{Fore.RED}{Style.BRIGHT}Scanning {Fore.GREEN}{Style.BRIGHT}{ip}{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.BLUE}{Style.BRIGHT}With Optimal System Resources{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")  # Printing a message indicating the start of the scan
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}  # Initializing a dictionary to store the open ports
    distribute_work(ip, open_ports)  # Performing the distributed work to update the open_ports dictionary

    # Quick Scan
    open_ports = quick_scan(ip, nm)  # Performing the quick scan and getting the open ports
    print(f"{Fore.GREEN}{Style.BRIGHT}Quick Scan Completed.{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}Identified Open Ports:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['tcp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}(TCP),{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['udp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}(UDP){Style.RESET_ALL}")  # Printing the identified open ports

    # Detailed Scan on Open Ports
    detailed_results = {} # Initializing a dictionary to store the detailed scan results in a dictionary object containing the details of the open ports discovered in the database
    if open_ports: # Initializing a dictionary to store the detailed scan results in a dictionary object containing the details of the open ports discovered in the database
        detailed_results = distribute_work(ip, open_ports)  # Performing the distributed work on the identified open ports

    def print_warning(message: str):
        if sys.stdout.isatty():
            print(f"{message}")
        else:
            print(f"WARNING: {message}")

    report_filename = os.path.join("C:\\Users\\MrDra\\OneDrive\\Desktop\\PythonTools", f"nmapscan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")
    with open(report_filename, "w") as report_file:
        for proto, ports_info in detailed_results.items():
            report_file.write(f"{proto.upper()} Ports:\n")
            for port, info in ports_info.items():
                if info:
                    state = info.get("state", "N/A")
                    service = info.get("name", "Unknown service")
                    product = info.get("product", "")
                    version = info.get("version", "")
                    extra = info.get("extrainfo", "")
                    reason = info.get("reason", "")
                    osclass = info.get("osclass", "")
                    osmatch = info.get("osmatch", "")
                    osfamily = info.get("osfamily", "")
                    script_info = info.get("script", {})
                    if isinstance(script_info, dict):
                        script_output = "\n".join([f"{str(k)}: {str(v)}" if 'vuln' not in str(k).lower() and 'cve' not in str(k).lower() else f"{str(k)}: {str(v)}" for k, v in script_info.items()])  # Formatting the script output
                    else:
                        script_output = ""
                    report_line = f"Port {port} {state}: {service} {product} {version} {extra} {reason} {osclass} {osmatch} {osfamily}\nScript Output:\n{script_output}\n\n"
                    if 'vuln' in script_output.lower() or 'cve' in script_output.lower():
                        report_file.write(f"WARNING: Vulnerabilities or CVEs detected!\n")
                        print_warning("Vulnerabilities or CVEs detected!")
                    report_file.write(report_line)
    print(f"{Fore.CYAN}{Style.BRIGHT}Detailed report saved to{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{report_filename}{Style.RESET_ALL}")

    # Save scan results in JSON format for the vulnerability scanning script
    results_json_path = os.path.join("C:\\Users\\MrDra\\OneDrive\\Desktop\\PythonTools", f"nmapscan_results_{time.strftime('%Y%m%d%H%M%S')}.json") # Generating the JSON file path for the vulnerability scanning script
    with open(results_json_path, 'w') as json_file: # Opening the JSON file in write mode
        json.dump(detailed_results, json_file, indent=4) # Writing the detailed scan results to the JSON file with indentation
    print(f"{Fore.BLUE}{Style.BRIGHT}Detailed report saved to {Fore.YELLOW}{Style.BRIGHT}{results_json_path}{Style.RESET_ALL}") # Printing the filename of the saved JSON file for the vulnerability scanning script with indentation and indent level of 4
    
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
