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
from colorama import Fore, Style  # Importing the colorama library for colored terminal output

# Ensure Nmap is available
try:
    nm = nmap.PortScanner()  # Creating an instance of the PortScanner class from the nmap library
except nmap.PortScannerError as e:
    print(f"{Fore.RED}Nmap not found: {e}{Style.RESET_ALL}")  # Printing an error message if Nmap is not found
    sys.exit(1)  # Exiting the program with a non-zero exit code
except Exception as e:
    print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")  # Printing an unexpected error message
    sys.exit(1)  # Exiting the program with a non-zero exit code

@contextlib.contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = fnull, fnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

CPU_CORES = multiprocessing.cpu_count() or 1  # Getting the number of CPU cores or defaulting to 1 if not available

def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))  # Connecting to a dummy IP address to get the local IP
            local_ip = s.getsockname()[0]  # Getting the local IP address
    except Exception:
        local_ip = '127.0.0.1'  # Defaulting to localhost IP if an error occurs
    return local_ip

def quick_scan(ip: str, nm: nmap.PortScanner) -> Dict[str, List[int]]:
    # Perform quick scan for TCP and UDP ports
    print(f"{Fore.YELLOW}Performing quick scan for TCP and UDP ports...{Style.RESET_ALL}")  # Printing a message indicating the start of the quick scan
    arguments = "-T3 --open"  # Setting the Nmap scan arguments
    nm.scan(hosts=ip, ports="1-65535", arguments=arguments)  # Scanning the specified IP address for open ports
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}  # Initializing a dictionary to store the open ports
    for proto in nm[ip].all_protocols():
        # Scanning individual ports for each protocol
        print(f"{Fore.CYAN}Scanning {proto.upper()} ports...{Style.RESET_ALL}")  # Printing a message indicating the start of scanning for a specific protocol
        for port in tqdm(sorted(nm[ip][proto].keys()), desc=f"Quick scanning {proto.upper()} ports"):  # Creating a progress bar for scanning the ports
            if nm[ip][proto][port]['state'] == 'open':
                open_ports[proto].append(port)  # Adding the open port to the dictionary
    return open_ports

def scan_port(ip: str, port: int, proto: str, nm: nmap.PortScanner) -> Tuple[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    arguments = "-T3 -sV -sC -A -O --version-intensity 9 --script=banner,malware,vuln"  # Setting the Nmap scan arguments
    nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)  # Scanning the specified port for detailed information
    scan_info = nm[ip].get(proto, {}).get(port, {})  # Getting the scan information for the port
    result = {
        "state": scan_info.get('state', 'closed'),  # Getting the state of the port (open or closed)
        "name": scan_info.get('name', ''),  # Getting the name of the service running on the port
        "product": scan_info.get('product', ''),  # Getting the product information of the service
        "version": scan_info.get('version', ''),  # Getting the version information of the service
        "extrainfo": scan_info.get('extrainfo', ''),  # Getting additional information about the service
        "reason": scan_info.get('reason', ''),  # Getting the reason for the port state
        "script": scan_info.get('script', {})  # Getting the script output for the port
    }
    return port, result

def worker(ip: str, ports: List[int], proto: str, nm: nmap.PortScanner) -> Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = {}  # Initializing a dictionary to store the scan results
    for port in tqdm(ports, desc=f"Scanning {proto.upper()} ports {ports[0]}-{ports[-1]}", leave=False):  # Creating a progress bar for scanning the ports
        port_result = scan_port(ip, port, proto, nm)  # Scanning the port and getting the result
        if port_result[1]:
            results[port_result[0]] = port_result[1]  # Adding the scan result to the dictionary
    return results

def distribute_work(ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}  # Initializing a dictionary to store the detailed scan results
    proto = None  # Initialize proto to a default value
    with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_CORES) as executor:  # Creating a thread pool executor
        futures: List[concurrent.futures.Future[Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]]] = []  # Initializing a list to store the futures
        for proto, ports in open_ports.items():
            if ports:
                # Perform detailed scan on open ports for each protocol
                print(f"{Fore.YELLOW}Performing detailed {proto.upper()} scan on open ports...{Style.RESET_ALL}")  # Printing a message indicating the start of the detailed scan
                for port in ports:
                    nm_copy = copy.deepcopy(nm)  # Creating a deep copy of the PortScanner object for each thread
                    futures.append(executor.submit(worker, ip, [port], proto, nm_copy))  # Submitting the worker function to the executor

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Detailed Scanning Progress", unit="port"):  # Creating a progress bar for the completed futures
            proto_results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = future.result()  # Getting the result of the future
            if proto is not None and proto not in detailed_results:
                detailed_results[proto] = {}  # Adding the protocol to the detailed results dictionary if not present
            for port, result in proto_results.items():
                if proto is not None and result is not None:  # Ensure result is not None before assigning it
                    detailed_results[proto][port] = result  # Adding the result to the detailed results dictionary

    # Print the detailed scan results
    for proto, ports_info in detailed_results.items():
        print(f"\n{Fore.CYAN}{proto.upper()} Ports:{Style.RESET_ALL}")  # Printing the protocol name
        for port, info in ports_info.items():
            print(f"Port {port}:")  # Printing the port number
            print(f"  State: {info.get('state')}")  # Printing the state of the port
            print(f"  Name: {info.get('name')}")  # Printing the name of the service running on the port
            print(f"  Product: {info.get('product')}")  # Printing the product information of the service
            print(f"  Version: {info.get('version')}")  # Printing the version information of the service
            print(f"  Extra Info: {info.get('extrainfo')}")  # Printing additional information about the service
            print(f"  Reason: {info.get('reason')}")  # Printing the reason for the port state
            print(f"  Script Output:")  # Printing the script output for the port
            script_info = info.get('script')
            if isinstance(script_info, dict):
                for key, value in script_info.items():
                    if 'vuln' in key.lower() or 'cve' in key.lower():
                        print(f"    {Fore.RED}{Style.BRIGHT}{key}: {value}{Style.RESET_ALL}")  # Printing the script output with highlighting for vulnerabilities or CVEs
                print()
            else:
                print(f"    No script output\n")  # Printing a message if there is no script output

    return detailed_results

def main():
    ip = get_local_ip()  # Getting the local IP address
    print(f"{Fore.GREEN}Scanning {ip} using optimal system resources...{Style.RESET_ALL}")  # Printing a message indicating the start of the scan
    start_time = time.time()  # Getting the start time of the scan
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}  # Initializing a dictionary to store the open ports
    distribute_work(ip, open_ports)  # Performing the distributed work to update the open_ports dictionary

    # Quick Scan
    print(f"\n{Fore.RED}Starting quick scan...{Style.RESET_ALL}")  # Printing a message indicating the start of the quick scan
    open_ports = quick_scan(ip, nm)  # Performing the quick scan and getting the open ports
    print(f"{Fore.GREEN}Quick scan completed. Identified open ports: {Style.BRIGHT}{Fore.RED}{', '.join(map(str, open_ports['tcp']))}{Style.RESET_ALL}{Fore.GREEN} (TCP), {Style.BRIGHT}{Fore.RED}{', '.join(map(str, open_ports['udp']))}{Style.RESET_ALL}{Fore.GREEN} (UDP){Style.RESET_ALL}")  # Printing the identified open ports

    # Detailed Scan on Open Ports
    detailed_results = {}
    if open_ports:
        print(f"\n{Fore.CYAN}Starting detailed scan on identified open ports...{Style.RESET_ALL}")  # Printing a message indicating the start of the detailed scan
        detailed_results = distribute_work(ip, open_ports)  # Performing the distributed work on the identified open ports

    # Output results to a file
    report_filename = os.path.join("C:\\Users\\MrDra\\OneDrive\\Desktop\\PythonTools", f"nmap_scan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")  # Generating the report filename
    with open(report_filename, "w") as report_file:
        for proto, ports_info in detailed_results.items():
            report_file.write(f"{Fore.YELLOW}{proto.upper()} Ports:{Style.RESET_ALL}\n")  # Writing the protocol name to the report file
            for port, info in ports_info.items():
                if info:  # Ensure there's information to write
                    state = info.get("state", "N/A")  # Getting the state of the port
                    service = info.get("name", "Unknown service")  # Getting the name of the service running on the port
                    product = info.get("product", "")  # Getting the product information of the service
                    version = info.get("version", "")  # Getting the version information of the service
                    extra = info.get("extrainfo", "")  # Getting additional information about the service
                    reason = info.get("reason", "")  # Getting the reason for the port state
                    script_info = info.get("script", {})  # Getting the script output for the port
                    if isinstance(script_info, dict):
                        script_output = "\n".join([f"{str(k)}: {str(v)}" if 'vuln' not in str(k).lower() and 'cve' not in str(k).lower() else f"{Fore.RED}{Style.BRIGHT}{str(k)}: {str(v)}{Style.RESET_ALL}" for k, v in script_info.items()])  # Formatting the script output
                    else:
                        script_output = ""
                    report_line = f"Port {port}/TCP {state}: {service} {product} {version} {extra} {reason}\nScript Output:\n{script_output}\n\n"  # Generating the report line
                    if 'vuln' in script_output.lower() or 'cve' in script_output.lower():
                        report_file.write(f"{Fore.RED}{Style.BRIGHT}WARNING: Vulnerabilities or CVEs detected!{Style.RESET_ALL}\n")  # Writing a warning message to the report file if vulnerabilities or CVEs are detected
                    report_file.write(report_line)  # Writing the report line to the report file
    print(f"{Fore.RED}Detailed report saved to {report_filename}{Style.RESET_ALL}")  # Printing the filename of the saved report

    elapsed_time = time.time() - start_time  # Calculating the elapsed time of the scan
    print(f"\n{Fore.GREEN}Completed scan in {elapsed_time:.2f} seconds.{Style.RESET_ALL}")  # Printing the elapsed time

if __name__ == "__main__":
    main()
