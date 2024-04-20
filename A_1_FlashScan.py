#The file is called nmapscan.py I'll get around to making it into something thats not so monstorously monolithic and ghastly. It works though.

# IMPORTANT ########################################################################################################################
#Below you will have to set your own path to where the script is held in your directory: 
# LOOKE FOR AND EDIT> 
    # Output results to a file
    # report_filename = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")
# IMPORTANT ########################################################################################################################

#The vulnscan at the end is being built out and worked on currently
########################################################################################################################################################################
  # BELOW TOWARDS THE VERY BOTTOM COMMENTED OUT IS WHERE THE VULNSCAN.PY SCRIPT WOULD TAKE THE JSON FILE FROM THE NMAPSCAN.PY SCAN AND WORK ON THE FINDINGS USING NVD 
  # API URL TO DIG FURTHER. 
  # WILL FINISH CREATING AND TESTING THIS BUT FOR NOW IF YOU CREATE A VULNSCAN.PY SCRIPT THIS WILL WORK WITH THAT AND TAKE IN THE JSON FILE THAT THE NMAPSCAN.PY CREATES
  # FOR NOW IT WILL BE COMMENTED OUT BUT THE NMAPSCAN.PY WORKS FINE AS A STANDALONE
########################################################################################################################################################################

import nmap  # Importing the nmap library for network scanning
import concurrent.futures  # Importing the concurrent.futures module for parallel execution
import socket  # Importing the socket module for network communication
import os  # Importing the os module for interacting with the operating system
import sys  # Importing the sys module for system-specific parameters and functions
import multiprocessing  # Importing the multiprocessing module for utilizing multiple CPU cores
import contextlib  # Importing the contextlib module for context management utilities
import time  # Importing the time module for time-related functions
from typing import Dict, List, Tuple, Union, Optional # Importing type hints for function signatures
import copy  # Importing the copy module for creating deep copies of objects
import json # Importing the json module for serialization and deserialization of objects and functions from JSON files
import xml.etree.ElementTree as ET
import subprocess # Importing the subprocess module for serialization and deserialization of objects and functions from JSON files
from halo import Halo  # type: ignore
from multiprocessing import cpu_count, Pool
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init  # Importing the colorama library for colored terminal output
init(autoreset=True) # Initializing colorama for auto-resetting colors after each print statement

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

CPU_CORES = multiprocessing.cpu_count() or 1 + 4  # Getting the number of CPU cores or defaulting to 1 if Not Available

def get_local_ip() -> str: # Defining a function to get the local IP address of the current process and return it as a string in the format expected by the current process and previous process manager
    try: # Using a try block to handle exceptions
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: # Creating a socket object for network communication
            s.connect(('10.255.255.255', 1))  # Connecting to a dummy IP address to get the local IP
            local_ip = s.getsockname()[0]  # Getting the local IP address
    except Exception: # Handling exceptions that may occur while getting the local IP address
        local_ip = '127.0.0.1'  # Defaulting to localhost IP if an error occurs
    return local_ip # Returning the local IP address as a string

def scan_port(ip: str, port: int, proto: str, nm: nmap.PortScanner) -> Tuple[int, Dict[str, Union[str, List[str], Dict[str, str]]]]:
    def get_field_name(key: str, synonyms_dict: Dict[str, List[str]]) -> Optional[str]:
        for field, synonyms in synonyms_dict.items():
            if key.lower() in [synonym.lower() for synonym in synonyms]:
                return field
        return None
    def process_certificate(cert_text: str) -> List[str]:
        """Process the SSL certificate output from nmap."""
        return cert_text.splitlines()
    def process_scripts(scripts: Dict[str, str]) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        """Process and return structured data from script outputs."""
        processed_scripts: Dict[str, Union[str, List[str], Dict[str, str]]] = {}
        for script_name, output in scripts.items():
            if 'vuln' in script_name:
                processed_scripts['vulnerabilities'] = parse_vuln_output(output)
            else:
                processed_scripts[script_name] = output
        return processed_scripts
    def parse_vuln_output(output: str) -> str:
        """Extract and format vulnerability data from script output."""
        return output
    arguments = "-T3 -sV -A -O --version-intensity 9 --script=default,vuln,banner,http-headers,http-title,vulners -PE -PP -PM -PS21,23,80,3389 -PA80,443,8080 -vvv"
    nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)
    scan_info = nm[ip].get(proto, {}).get(port, {})
    field_synonyms = {
        "state": ["state", "status", "condition", "stature", "standing", "state_of_play", "context", "situation", "phase"],
        "name": ["name", "moniker", "denomination", "appellation", "nomenclature", "term", "designation", "title", "alias"],
        "product": ["product", "item", "goods", "merchandise", "commodity", "article", "unit", "model", "make"],
        "version": ["version", "revision", "variant", "edit", "update", "upgrade", "release", "edition", "build"],
        "address": ["address", "location", "place", "point", "site", "spot", "locale", "position", "setting"],
        "machine": ["machine", "engine", "apparatus", "mechanism", "contraption", "device", "gadget", "instrument", "tool"],
        "memory": ["memory", "storage", "capacity", "cache", "buffer", "bank", "reservoir", "store", "repository"],
        "mac": ["mac", "media_access_control", "ethernet_address", "network_address", "physical_address", "hardware_id", "nic_address", "adapter_address", "link_address"],
        "mac_vendor": ["mac_vendor", "manufacturer", "brand", "producer", "maker", "fabricator", "builder", "creator", "supplier"],
        "device": ["device", "gadget", "appliance", "instrument", "tool", "machinery", "equipment", "apparatus", "hardware"],
        "network": ["network", "net", "system", "grid", "web", "mesh", "matrix", "plexus", "complex"],
        "extrainfo": ["extrainfo", "details", "data", "particulars", "information", "insights", "specifics", "facts", "figures"],
        "reason": ["reason", "cause", "basis", "rationale", "motive", "justification", "grounds", "explanation", "purpose"],
        "osclass": ["osclass", "operating_system_class", "os_family", "os_type", "os_category", "system_type", "platform_type", "os_group", "os_series"],
        "osfamily": ["osfamily", "os_lineage", "os_kind", "system_family", "platform_family", "os_branch", "os_grouping", "os_genus", "os_order"],
        "hostname": ["hostname", "host_id", "server_name", "node_name", "machine_name", "dns_name", "computer_name", "system_name", "network_name"],
        "hostnames": ["hostnames", "host_ids", "server_names", "node_names", "machine_names", "dns_names", "computer_names", "system_names", "network_names"],
        "hostname_type": ["hostname_type", "host_category", "server_class", "machine_kind", "node_type", "name_category", "system_class", "network_type", "domain_type"],
        "ipv4": ["ipv4", "ipv4_address", "inet4_address", "ipv4_loc", "ipv4_site", "ipv4_node", "ipv4_zone", "ipv4_region", "ipv4_sector"],
        "ipv6": ["ipv6", "ipv6_address", "inet6_address", "ipv6_loc", "ipv6_site", "ipv6_node", "ipv6_zone", "ipv6_region", "ipv6_sector"],
        "ipv4_id": ["ipv4_id", "ipv4_ident", "ipv4_tag", "ipv4_code", "ipv4_mark", "ipv4_num", "ipv4_ref", "ipv4_index", "ipv4_label"],
        "ipv6_id": ["ipv6_id", "ipv6_ident", "ipv6_tag", "ipv6_code", "ipv6_mark", "ipv6_num", "ipv6_ref", "ipv6_index", "ipv6_label"],
        "osgen": ["osgen", "os_generation", "os_release", "os_version", "os_build", "os_revision", "os_cycle", "os_wave", "os_period"],
        "osaccuracy": ["osaccuracy", "os_precision", "os_certainty", "os_exactness", "os_fidelity", "os_reliability", "os_precision_level", "os_accuracy_grade", "os_exact_measure"],
        "osmatch": ["osmatch", "os_compatibility", "os_correspondence", "os_conformity", "os_alignment", "os_agreement", "os_parallels", "os_similarity", "os_congruence"],
        "vlan_id": ["vlan_id", "vlan_tag", "vlan_code", "vlan_mark", "vlan_label", "vlan_number", "vlan_index", "vlan_identifier", "vlan_ref"],
        "vlan_name": ["vlan_name", "vlan_designation", "vlan_title", "vlan_alias", "vlan_nomenclature", "vlan_label", "vlan_denomination", "vlan_term", "vlan_identifier"],
        "distance": ["distance", "range", "span", "reach", "length", "stretch", "expanse", "interval", "separation"],
        "tcp_sequence": ["tcp_sequence", "tcp_seq", "sequence_number", "tcp_order", "tcp_progression", "tcp_chain", "tcp_series", "tcp_succession", "tcp_continuum"],
        "tcp_options": ["tcp_options", "tcp_prefs", "tcp_settings", "tcp_choices", "tcp_flags", "tcp_configurations", "tcp_parameters", "tcp_modes", "tcp_alternatives"],
        "service_info": ["service_info", "service_data", "service_details", "service_facts", "service_specifics", "service_statistics", "service_insights", "service_intelligence", "service_records"],
        "script": ["script", "script_code", "nse_output", "automation_code", "routine", "procedure", "batch_script", "script_file", "executable_script"]
    }
    # Process and map nmap results to fields dynamically
    result: Dict[str, Union[str, List[str], Dict[str, str]]] = {}
    for key, value in scan_info.items():
        field_name = get_field_name(key, field_synonyms)
        if field_name:
            result[field_name] = value
        else:
            result[key] = value  # Keep original if no synonym found
    if 'ssl-cert' in scan_info:
        cert_details = process_certificate(scan_info['ssl-cert'])
        result['cert'] = cert_details
    if 'script' in scan_info:
        script_outputs = process_scripts(scan_info['script'])
        result.update(script_outputs)
    result = {
        "state": scan_info.get('state', 'closed'),
        "name": scan_info.get('name', ''),
        "product": scan_info.get('product', ''),
        "version": scan_info.get('version', ''),
        "address": scan_info.get('address', ''),
        "machine": scan_info.get('machine', ''),
        "memory": scan_info.get('memory', ''),
        "mac": scan_info.get('mac', ''),
        "mac_vendor": scan_info.get('mac_vendor', ''),
        "device": scan_info.get('device', ''),
        "network": scan_info.get('network', ''),
        "extrainfo": scan_info.get('extrainfo', ''),
        "reason": scan_info.get('reason', ''),
        "osclass": scan_info.get('osclass', ''),
        "osfamily": scan_info.get('osfamily', ''),
        "hostname": scan_info.get('hostname', ''),
        "hostnames": scan_info.get('hostnames', ''),
        "hostname_type": scan_info.get('hostname_type', ''),
        "ipv4": scan_info.get('ipv4', ''),
        "ipv6": scan_info.get('ipv6', ''),
        "ipv4_id": scan_info.get('ipv4_id', ''),
        "ipv6_id": scan_info.get('ipv6_id', ''),
        "osgen": scan_info.get('osgen', ''),
        "osaccuracy": scan_info.get('osaccuracy', ''),
        "osmatch": scan_info.get('osmatch', ''),
        "vlan_id": scan_info.get('vlan_id', ''),
        "vlan_name": scan_info.get('vlan_name', ''),
        "distance": scan_info.get('distance', ''),
        "tcp_sequence": scan_info.get('tcp_sequence', ''),
        "tcp_options": scan_info.get('tcp_options', ''),
        "service_info": scan_info.get('service_info', ''),
        "script": scan_info.get('script', {})
    } if scan_info else {}
    return port, result

def quick_scan(ip: str, nm: nmap.PortScanner) -> Dict[str, List[int]]:
    print(f"{Fore.YELLOW}{Style.BRIGHT}Setting Up Initial Scan On {Fore.RED}{Style.BRIGHT}{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}SYSTEM{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")
    # Updated arguments to include multiple ICMP probes
    arguments = "-T5 --version-intensity 9 --open -PE -PP -PM -PS21,23,80,3389 -PA80,443,8080"
    nm.scan(hosts=ip, ports="1-65535", arguments=arguments)
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
    spinner = Halo(text='Scanning ports', spinner='dots')
    spinner.start(text=None)  # type: ignore
    for proto in nm[ip].all_protocols():
        ports = sorted(nm[ip][proto].keys())
        total_ports = len(ports)
        completed = 0
        max_workers = (os.cpu_count() or 1) + 4
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
    with Pool(processes=(cpu_count() or 1) + 4) as pool:
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
    max_workers = (cpu_count() or 1) + 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(scan_and_update, ports, [ip]*len(ports), [proto]*len(ports), [nm]*len(ports), [spinner]*len(ports), [completed]*len(ports), [results]*len(ports))
    return results

scan_info = {}  # Add this line at the appropriate place in your code
def distribute_work(ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]:# Define scan_info here or get its value from somewhere
    init()
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
                spinner.start(text=None) # type: ignore
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
        """Prints warnings in red."""
        print(f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}")

    def print_certificate(cert_text: str):
        """Prints certificate details, highlighting the BEGIN and END markers."""
        cert_lines = cert_text.split('\n')
        for line in cert_lines:
            if "BEGIN CERTIFICATE" in line or "END CERTIFICATE" in line:
                print(f"{Fore.YELLOW}{Style.BRIGHT}{line}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")

    # Terminal output
    for ports_info in detailed_results.values():
        for port, info in ports_info.items():
            if info:  # Check if info is not empty
                print(f"{Fore.BLUE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")
            # For each field, check if it exists in info and if it's not empty
            fields = ['state', 'name', 'product', 'version', 'address', 'machine', 'memory', 'mac', 'mac_vendor', 'device', 'network', 'extrainfo', 'reason', 'osclass', 'osmatch', 'osfamily', 'hostname', 'hostnames', 'hostname_type', 'ipv4', 'ipv6', 'ipv4_id', 'ipv6_id', 'osgen', 'osaccuracy', 'osmatch', 'vlan_id', 'vlan_name', 'distance', 'tcp_sequence', 'tcp_options', 'service_info']
            for field in fields:
                if field in info and info[field] not in ['', 'Not available', 'None']:  # Check if field is in info and if it's not empty
                    if field == 'state':
                        print(f"{Fore.GREEN}{Style.BRIGHT}State{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{info['state']}{Style.RESET_ALL}")
                    elif field == 'name':
                        print(f"{Fore.BLUE}{Style.BRIGHT}Name{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{info['name']}{Style.RESET_ALL}")
                    elif field == 'product':
                        print(f"{Fore.BLUE}{Style.BRIGHT}Product{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{info['product']}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{field.capitalize()}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{info[field]}{Style.RESET_ALL}")
            # Script-Output Info
            print(f"{Fore.YELLOW}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.BLUE}{Style.BRIGHT}NMAP Scripts Output Below If Found{Style.RESET_ALL}{Fore.YELLOW}{Style.BRIGHT}]{Style.RESET_ALL}")
            script_info = info.get('script', {})
            if isinstance(script_info, dict):
                for key, value in script_info.items():
                    if 'vuln' in key.lower() or 'cve' in key.lower():
                        print_warning(f"{Fore.BLACK}{Style.BRIGHT}[[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}-WARNING-{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}]]{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT} VULNs ~OR~ CVEs DETECTED!{Style.RESET_ALL} {Fore.BLACK}{Style.BRIGHT}[[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}-WARNING-{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}]]{Style.RESET_ALL}")
                        print_warning(f"{Fore.RED}{key}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}")
                    elif 'certificate' in key.lower():
                        print_certificate(value)
                    elif 'csrf' in key.lower():
                        print(f"{Fore.RED}{key}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}")
                    elif 'ssl-enum-ciphers' in key.lower():
                        print(f"{Fore.RED}SSL Ciphers{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}")
                    elif 'ssh2-enum-algos' in key.lower():
                        print(f"{Fore.RED}SSH2 Algorithms{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}")
                    elif 'http-enum' in key.lower():
                        print(f"{Fore.YELLOW}HTTP Directories And Files{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{Style.BRIGHT}{key}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{value}{Style.RESET_ALL}")
                print()
            else:
                print(f"{Fore.RED}No script output\n{Style.RESET_ALL}")
    return detailed_results

def main():
    ip = get_local_ip()
    print(f"{Fore.RED}{Style.BRIGHT}Scanning {Fore.GREEN}{Style.BRIGHT}{ip}{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.BLUE}{Style.BRIGHT}With Optimal System Resources{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
    nm = nmap.PortScanner()
    # Quick Scan
    open_ports = quick_scan(ip, nm)  # Performing the quick scan and getting the open ports
    print(f"{Fore.GREEN}{Style.BRIGHT}Quick Scan Completed.{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}Identified Open Ports:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['tcp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}(TCP),{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['udp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}(UDP){Style.RESET_ALL}")  # Printing the identified open ports
    # Detailed Scan on Open Ports
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}
    if open_ports: # Initializing a dictionary to store the detailed scan results in a dictionary object containing the details of the open ports discovered in the database
        detailed_results = distribute_work(ip, open_ports) # Performing the distributed work on the identified open ports


    # Save scan results in TEXT format for the vulnerability scanning script
    keys_to_ignore = []  # Define keys_to_ignore here
    report_filename = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")
    # Text file output
    with open(report_filename, "w") as report_file:
        for _, ports_info in detailed_results.items():  # Ignore the protocol
            for port, info in ports_info.items():
                if any(key not in keys_to_ignore for key in info.keys()):
                    report_file.write(f"Port {port}:\n")
                for field in ['state', 'name', 'product', 'version', 'address', 'machine', 'memory', 'mac', 'mac_vendor', 'device', 'network', 'extrainfo', 'reason', 'osclass', 'osfamily', 'hostname', 'hostnames', 'hostname_type', 'ipv4', 'ipv6', 'ipv4_id', 'ipv6_id', 'osgen', 'osaccuracy', 'osmatch', 'vlan_id', 'vlan_name', 'distance', 'tcp_sequence', 'tcp_options', 'service_info']:
                    value = info.get(field)
                    if value and value not in ['Not available', 'None']:
                        report_file.write(f"  {field.capitalize()}: {value}\n")
                report_file.write(f"  Script Output:\n")
                script_info = info.get('script', {})
                script_output = ''
                if isinstance(script_info, dict):
                    for key, value in script_info.items():
                        if 'vuln' in key.lower() or 'cve' in key.lower():
                            report_file.write(f"  [[-WARNING-]] VULNs ~OR~ CVEs DETECTED! [[-WARNING-]]\n  {key}: {value}\n")
                        elif 'certificate' in key.lower():
                            report_file.write(f"  Certificate: {value}\n")
                        elif 'csrf' in key.lower():
                            report_file.write(f"  CSRF: {value}\n")
                        elif 'ssl-enum-ciphers' in key.lower():
                            report_file.write(f"  SSL Ciphers: {value}\n")
                        elif 'ssh2-enum-algos' in key.lower():
                            report_file.write(f"  SSH2 Algorithms: {value}\n")
                        elif 'http-enum' in key.lower():
                            report_file.write(f"  HTTP Directories and Files: {value}\n")
                        else:
                            report_file.write(f"  {key}: {value}\n")
                        script_output += value
                report_file.write("\n")
        print(f"{Fore.CYAN}{Style.BRIGHT}Detailed TEXT Report Saved To{Fore.YELLOW}{Style.BRIGHT}{report_filename}{Style.RESET_ALL}")

    # Save scan results in JSON format for the vulnerability scanning script
    results_json_path = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_results_{time.strftime('%Y%m%d%H%M%S')}.json") # Generating the JSON file path for the vulnerability scanning script
    try:
        organized_results = {}
        for _, ports_info in detailed_results.items():  # Ignore the protocol
            for port, info in ports_info.items():
                # Filter out keys with empty values
                filtered_info = {k: v for k, v in info.items() if v}
                if 'script' in filtered_info:
                    script_info = filtered_info['script']
                    if isinstance(script_info, dict):
                        for key, value in script_info.items():
                            if 'vuln' in key.lower() or 'cve' in key.lower():
                                filtered_info['warning'] = '[[-WARNING-]] VULNs ~OR~ CVEs DETECTED! [[-WARNING-]]'
                                break
                if port not in organized_results:
                    organized_results[port] = []
                organized_results[port].append(filtered_info)  # type: ignore # Remove the protocol from the dictionary
        with open(results_json_path, 'w') as json_file: # Opening the JSON file in write mode
            json.dump(organized_results, json_file, indent=4) # Writing the organized scan results to the JSON file with indentation
        print(f"{Fore.CYAN}{Style.BRIGHT}Detailed JSON Report Saved To{Fore.RED}{Style.BRIGHT}{results_json_path}{Style.RESET_ALL}") # Printing the filename of the saved JSON file for the vulnerability scanning script with indentation and indent level of 4
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}An error occurred while saving the detailed report: {str(e)}{Style.RESET_ALL}")

    # Define the path for the XML file
    xml_path = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_results_{time.strftime('%Y%m%d%H%M%S')}.xml")
    # Ensure the directory exists
    os.makedirs(os.path.dirname(xml_path), exist_ok=True)
    # Create the root element of the XML structure
    root = ET.Element("NmapScanResults")
    # Iterate over the detailed_results dictionary
    for _, ports_info in detailed_results.items():  # Ignore the protocol
        for port, info in ports_info.items():
            # Create an XML element for each port
            port_elem = ET.SubElement(root, "Port")
            port_elem.set("id", str(port))
            # Filter out keys with empty values
            filtered_info = {k: v for k, v in info.items() if v and v not in ['Not available', 'None']}
            # Create XML elements for each piece of information                            warning_created = False
            for key, value in filtered_info.items():
                if isinstance(value, dict):
                    # For nested dictionaries, we will flatten the structure
                    for subkey, subvalue in value.items():
                        if subvalue and subvalue not in ['Not available', 'None']:
                            sub_elem = ET.SubElement(port_elem, key + subkey.replace('_', '').capitalize())
                            sub_elem.text = str(subvalue)
                elif isinstance(value, list):
                    # For lists, we join the items into a single string
                    list_elem = ET.SubElement(port_elem, key.replace('_', '').capitalize())
                    list_elem.text = ', '.join(value)
                else:
                    # Directly assign the value
                    info_elem = ET.SubElement(port_elem, key.replace('_', '').capitalize())
                    info_elem.text = str(value)
                    # Check if the value contains 'vuln' or 'cve'
                warning_created = False
                if not warning_created and ('vuln' in str(value).lower() or 'cve' in str(value).lower()):
                    warning_elem = ET.SubElement(port_elem, "Warning")
                    warning_elem.text = "[[-WARNING-]] VULNs ~OR~ CVEs DETECTED! [[-WARNING-]]"
                    warning_created = True
    # Save the XML structure to the specified XML file path
    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
    print(f"{Fore.CYAN}{Style.BRIGHT}Detailed XML Report Saved To{Fore.BLUE}{Style.BRIGHT}{xml_path}{Style.RESET_ALL}")

########################################################################################################################################################################
  # BELOW COMMENTED OUT IS WHERE THE VULNSCAN.PY SCRIPT WOULD TAKE THE JSON FILE FROM THE NMAPSCAN.PY SCAN AND WORK ON THE FINDINGS USING NVD 
  # API URL TO DIG FURTHER. 
  # WILL FINISH CREATING AND TESTING THIS BUT FOR NOW IF YOU CREATE A VULNSCAN.PY SCRIPT THIS WILL WORK WITH THAT AND TAKE IN THE JSON FILE THAT THE NMAPSCAN.PY CREATES
  # FOR NOW IT WILL BE COMMENTED OUT BUT THE NMAPSCAN.PY WORKS FINE AS A STANDALONE
########################################################################################################################################################################
    
    # # Prompt user to initiate vulnerability scanning
    # user_input = input("Do you want to proceed with vulnerability scan? (y/n): ") # Prompting the user to initiate the vulnerability scan with y/n parameter values (y/n):
    # if user_input.lower() == 'y' or user_input.upper() == 'Y': # Checking if the user input is 'y' or 'Y'
    #     print("Proceeding with vulnerability scan...") # Prompting the user to proceed with the vulnerability scan
    #     # Assuming `results_json_path` holds the path to the JSON file from nmap scan
    #     vulnscan_script_path = os.path.join(os.path.dirname(__file__), "vulnscan.py") # Path to the vulnerability scanning script file
    #     output_dir = os.path.join(os.path.dirname(vulnscan_script_path), "vulnscan_results") # Directory to store the vulnerability scanning results file
    #     # Execute vulnscan.py script with real-time output
    #     try: # Using a try block to handle exceptions that may occur while executing the vulnerability scanning script
    #         command = ["python", vulnscan_script_path, results_json_path, output_dir] # Creating a command to execute the vulnerability scanning script with the JSON file path and output directory
    #         with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process: # Using the subprocess module to execute the vulnerability scanning script with real-time output instead of using the os.system() function
    #             while process.stdout is not None: # Checking if the output directory is not empty before reading the line from the output directory
    #                 line = process.stdout.readline() # Read the line from the output directory and convert it to a string
    #                 if not line: # Checking if the line is empty is not necessary as the loop will break if the line is empty
    #                     break # Ignore error and continue processing further lines from the output directory
    #                 print(line, end='') # print line from the output directory if it exists and is not empty
    #         process.wait()  # Wait for the process to complete
    #         if process.returncode != 0: # Checking if the process return code is not 0 means that the process encountered an error
    #             print(f"{Fore.RED}Vulnerability scan encountered an error.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script
    #     except Exception as e: # Handling exceptions that may occur while executing the vulnerability scanning script
    #         print(f"{Fore.RED}Failed to execute vulnscan.py: {e}{Style.RESET_ALL}") # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
    # else: # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
    #     print("Vulnerability scan aborted.") # Printing a message if the user chooses not to proceed with the vulnerability scan
    # if user_input.lower() == 'y' or user_input.upper() == 'Y': # Checking if the user input is 'y' or 'Y'
    #     print("Proceeding with vulnerability scan...") # Prompting the user to proceed with the vulnerability scan
    #     # Assuming `results_json_path` holds the path to the JSON file from nmap scan
    #     vulnscan_script_path = os.path.join(os.path.dirname(__file__), "vulnscan.py") # Path to the vulnerability scanning script file
    #     output_dir = os.path.join(os.path.dirname(vulnscan_script_path), "vulnscan_results") # Directory to store the vulnerability scanning results file

    #     # Execute vulnscan.py script with real-time output
    #     try: # Using a try block to handle exceptions that may occur while executing the vulnerability scanning script
    #         command = ["python", vulnscan_script_path, results_json_path, output_dir] # Creating a command to execute the vulnerability scanning script with the JSON file path and output directory
    #         with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process: # Using the subprocess module to execute the vulnerability scanning script with real-time output instead of using the os.system() function
    #             while process.stdout is not None: # Checking if the output directory is not empty before reading the line from the output directory
    #                 line = process.stdout.readline() # Read the line from the output directory and convert it to a string
    #                 if not line: # Checking if the line is empty is not necessary as the loop will break if the line is empty
    #                     break # Ignore error and continue processing further lines from the output directory
    #                 print(line, end='') # print line from the output directory if it exists and is not empty
    #         process.wait()  # Wait for the process to complete

    #         if process.returncode != 0: # Checking if the process return code is not 0 means that the process encountered an error
    #             print(f"{Fore.RED}Vulnerability scan encountered an error.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script
    #     except Exception as e: # Handling exceptions that may occur while executing the vulnerability scanning script
    #         print(f"{Fore.RED}Failed to execute vulnscan.py: {e}{Style.RESET_ALL}") # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
    # else: # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
    #     print("Vulnerability scan aborted.") # Printing a message if the user chooses not to proceed with the vulnerability scan

    # # Assuming `results_json_path` holds the path to the JSON file from nmap scan
    # if user_input.lower() == 'y' or user_input.upper() == 'Y': # Checking if the user input is 'y' or 'Y'
    #     print("Proceeding with vulnerability scan...") # Prompting the user to proceed with the vulnerability scan
    #     # Assuming `results_json_path` holds the path to the JSON file from nmap scan
    #     vulnscan_script_path = os.path.join(os.path.dirname(__file__), "vulnscan.py") # Path to the vulnerability scanning script file
    #     output_dir = os.path.join(os.path.dirname(vulnscan_script_path), "vulnscan_results") # Directory to store the vulnerability scanning results file

    #     # Execute vulnscan.py script with real-time output
    #     try: # Using a try block to handle exceptions that may occur while executing the vulnerability scanning script
    #         command = ["python", vulnscan_script_path, results_json_path, output_dir] # Creating a command to execute the vulnerability scanning script with the JSON file path and output directory
    #         with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process: # Using the subprocess module to execute the vulnerability scanning script with real-time output instead of using the os.system() function
    #             while process.stdout is not None: # Checking if the output directory is not empty before reading the line from the output directory
    #                 line = process.stdout.readline() # Read the line from the output directory and convert it to a string
    #                 if not line: # Checking if the line is empty is not necessary as the loop will break if the line is empty
    #                     break # Ignore error and continue processing further lines from the output directory
    #                 print(line, end='') # print line from the output directory if it exists and is not empty
    #         process.wait()  # Wait for the process to complete

    #         if process.returncode != 0: # Checking if the process return code is not 0 means that the process encountered an error
    #             print(f"{Fore.RED}Vulnerability scan encountered an error.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script
    #     except Exception as e: # Handling exceptions that may occur while executing the vulnerability scanning script
    #         print(f"{Fore.RED}Failed to execute vulnscan.py: {e}{Style.RESET_ALL}") # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
    # else: # Error handling is not necessary as the user input is validated before proceeding with the vulnerability scan
    #     print("Vulnerability scan aborted.") # Printing a message if the user chooses not to proceed with the vulnerability scan

    #             # Assuming `results_json_path` holds the path to the JSON file from nmap scan
    #     vulnscan_script_path = os.path.join(os.path.dirname(__file__), "vulnscan.py") # Path to the vulnerability scanning script file
    #     output_dir = os.path.join(os.path.dirname(vulnscan_script_path), "vulnscan_results") # Directory to store the vulnerability scanning results file

    #             # Create the output directory if it doesn't exist
    #     os.makedirs(output_dir, exist_ok=True) # Make sure output directory exists before running the vulnerability scanning script

    # Timing and final message
    elapsed_time = time.time() - start_time # Time difference between start_time and end_time for the last scan in seconds since the last time the script was run
    print(f"\n{Fore.GREEN}Total process completed in {elapsed_time:.2f} seconds.{Style.RESET_ALL}") # Reset all variables to their initial values before continuing to run vulnerability scanning script

if __name__ == "__main__": # Run the script if it is executed directly
    start_time = time.time()  # Record start time of the script
    main()


