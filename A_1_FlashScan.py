# This project is originally called nmapscan.py I'll get around to making it into something thats not so monstorously monolithic and ghastly. It works though.
# Works pretty fine and plenty of room for tinkering and tweaking. Have it it!

# IMPORTANT ########################################################################################################################
#Below you will have to set your own path to where the script is held in your directory: 
# LOOKE FOR AND EDIT THE THREE FILE OUTPUTS FOR TEXT, JSON & XML (Just CTL+F search this below) 
    # "C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE"
# IMPORTANT ########################################################################################################################
import nmap
import socket
import os
import sys
import contextlib
import importlib.util
import time
import copy
import json
import xml.etree.ElementTree as ET
import subprocess
from datetime import datetime
from colorama import Fore, Style, init
from halo import Halo  # type: ignore
import multiprocessing
from multiprocessing import cpu_count
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Union, Optional, Sequence
import re
import itertools
import threading

init(autoreset=True)  # Initializing colorama for auto-resetting colors after each print statement

# Global variables for logging
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"nmap_scan{time.strftime('%Y%m%d%H%M%S')}.log")
LOG_COLORS = {
    "DEBUG": "\033[1;34m",  # Bright Blue
    "INFO": "\033[1;35m",   # Bright Magenta
    "WARN": "\033[1;33m",   # Bright Yellow
    "ERROR": "\033[1;31m",  # Bright Red
    "FATAL": "\033[1;31m",  # Bright Red
    "NC": "\033[0m"         # No color (resets the color)
}

CPU_CORES = multiprocessing.cpu_count() or 1 + 4

def strip_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def log(log_priority: str, log_message: str):
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = LOG_COLORS.get(log_priority, LOG_COLORS["NC"])

    # Simplified console message
    console_message = f"{color}{log_message}{LOG_COLORS['NC']}"
    print(console_message)

    # Log to file
    try:
        file_message = f"{date_time} [{log_priority}] {strip_ansi_codes(log_message)}"
        with open(LOG_FILE, 'a') as file:
            file.write(f"{file_message}\n")
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}Failed to write log to file: {e}{Style.RESET_ALL}")

    # Exit if fatal error
    if log_priority == "FATAL":
        exit(1)

# Function to validate IP address
def is_valid_ip(ip: str) -> bool:
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def resolve_hostname(hostname: str) -> Optional[str]:
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Failed to resolve hostname: {hostname}{Style.RESET_ALL}")
        return None

def install_modules(modules: Sequence[Tuple[str, Optional[str]]]) -> None:
    def install_module(module_name: str, pip_name: Optional[str]):
        try:
            if pip_name:
                log("INFO", f"{Fore.YELLOW}{Style.BRIGHT}Installing{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{pip_name}{Style.RESET_ALL}{Fore.YELLOW}{Style.BRIGHT}...{Style.RESET_ALL}")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name])
            else:
                importlib.import_module(module_name)
        except ImportError as e:
            if pip_name:
                log("ERROR", f"{Fore.RED}{Style.BRIGHT}Failed to install{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{pip_name}{Style.RESET_ALL}. {Fore.RED}{Style.BRIGHT}Error:{Style.RESET_ALL} {e}. {Fore.RED}{Style.BRIGHT}Exiting...{Style.RESET_ALL}")
            else:
                log("ERROR", f"{Fore.RED}{Style.BRIGHT}Module{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{module_name}{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}is a built-in module and should not fail. Error:{Style.RESET_ALL} {e}. {Fore.RED}{Style.BRIGHT}Exiting...{Style.RESET_ALL}")
            sys.exit(1)

    max_workers = (cpu_count() or 1) + 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(install_module, module_name, pip_name) for module_name, pip_name in modules]
        for future in as_completed(futures):
            future.result()

# List of modules with corresponding pip install names
modules = [
    ('nmap', 'python-nmap'),
    ('socket', None),
    ('os', None),
    ('sys', None),
    ('contextlib', None),
    ('time', None),
    ('copy', None),
    ('json', None),
    ('xml.etree.ElementTree', 'xml'),
    ('subprocess', None),
    ('colorama', 'colorama'),
    ('halo', 'halo'),
    ('multiprocessing', None),
    ('concurrent.futures', None),
    ('typing', None)
]

# Detect and install missing modules
missing_modules = [(module_name, pip_name) for module_name, pip_name in modules if not importlib.util.find_spec(module_name)]
if missing_modules:
    install_modules(missing_modules)

# Ensure Nmap is available
try:
    nm = nmap.PortScanner()
except nmap.PortScannerError as e:
    print(f"{Fore.RED}{Style.BRIGHT}Nmap not found. Installing 'python-nmap'...{Style.RESET_ALL}")
    log("ERROR", f"{Fore.RED}{Style.BRIGHT}Nmap not found. Error: {e}. Installing 'python-nmap'...{Style.RESET_ALL}")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-nmap'])
    nm = nmap.PortScanner()
except Exception as e:
    print(f"{Fore.RED}{Style.BRIGHT}Unexpected error: {e}{Style.RESET_ALL}")
    log("FATAL", f"{Fore.RED}{Style.BRIGHT}Unexpected error: {e}{Style.RESET_ALL}")
    sys.exit(1)

@contextlib.contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = fnull, fnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
    except Exception as e:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Failed to obtain local IP, defaulting to localhost: {e}{Style.RESET_ALL}")
        local_ip = '127.0.0.1'
    return local_ip

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
            elif 'ssl-cert' in script_name:
                processed_scripts['ssl_cert'] = process_certificate(output)
            else:
                processed_scripts[script_name] = output
        return processed_scripts

    def parse_vuln_output(output: str) -> str:
        """Extract and format vulnerability data from script output."""
        return output

    arguments = "-sS -T3 -sV -A -O --version-intensity 9 --script=default,vuln,banner,http-headers,http-title,vulners -PE -PP -PM -PS21,23,80,3389 -PA80,443,8080 --data-length 10 -vvv"
    try:
        nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)
    except nmap.PortScannerError as e:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred while scanning port{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}{port}{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
    except Exception as e:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Unexpected error occurred while scanning port{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}{port}{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
        return port, {}

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
        "ip": ["ip", "ip_address", "address", "inet_address", "loc", "site", "node", "zone", "region", "sector"],
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
    arguments = "-T4 -O --version-intensity 9 --open -PE -PP -PM -PS21,23,80,3389 -PA80,443,8080 -vvv"

    spinner_text = ''.join([Fore.MAGENTA, Style.BRIGHT, 'INITIALIZING PRETTY SCAN', Style.RESET_ALL])
    spinners = [
        Halo(text=spinner_text, spinner='dots'),
        Halo(text=spinner_text, spinner='dots2'),
        Halo(text=spinner_text, spinner='dots3'),
        Halo(text=spinner_text, spinner='dots4'),
        Halo(text=spinner_text, spinner='dots5'),
        Halo(text=spinner_text, spinner='dots6'),
        Halo(text=spinner_text, spinner='dots7'),
        Halo(text=spinner_text, spinner='dots8'),
        Halo(text=spinner_text, spinner='dots9'),
        Halo(text=spinner_text, spinner='dots10'),
        Halo(text=spinner_text, spinner='dots11'),
        Halo(text=spinner_text, spinner='dots12')
    ]

    # Start each spinner in different colors
    colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
    for index, spinner in enumerate(spinners):
        color = colors[index % len(colors)]
        spinner.text = ''.join([color, Style.BRIGHT, 'INITIALIZING PRETTY SCAN', Style.RESET_ALL])
        spinner.start(text=None)  # type: ignore

    try:
        nm.scan(hosts=ip, ports="1-65535", arguments=arguments)
    except nmap.PortScannerError as e:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred during quick scan on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
        for spinner in spinners:
            spinner.stop()
        return {'tcp': [], 'udp': []}
    except Exception as e:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Unexpected error occurred during quick scan on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
        for spinner in spinners:
            spinner.stop()
        return {'tcp': [], 'udp': []}

    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
    for proto in nm[ip].all_protocols():
        ports = sorted(nm[ip][proto].keys())
        total_ports = len(ports)
        completed = 0
        max_workers = (os.cpu_count() or 1) + 4

        spinner = Halo(text=f'{Fore.GREEN}{Style.BRIGHT}Scanning {proto.upper()} Ports{Style.RESET_ALL}', spinner='dots')
        spinner.start(text=None)  # type: ignore

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(nm[ip][proto].get, port): port for port in ports}
            for future in as_completed(futures):
                port = futures[future]
                try:
                    result = future.result()
                    if result['state'] == 'open':
                        open_ports[proto].append(port)
                except Exception as e:
                    log("ERROR", f"\n{Fore.RED}{Style.BRIGHT}Error processing result for port{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}{port}{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
                completed += 1
                percentage = (completed / total_ports) * 100
                spinner.text = f'Scanned {completed} of {total_ports} ports ({percentage:.2f}%)'

        spinner.stop()

    for spinner in spinners:
        spinner.stop()

    return open_ports

def scan_all_open_ports(ip: str):
    nm = nmap.PortScanner()
    open_ports = quick_scan(ip, nm)
    if not open_ports['tcp'] and not open_ports['udp']:
        log("INFO", f"{Fore.YELLOW}{Style.BRIGHT}No open ports found on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}{Style.RESET_ALL}.")
        return

    spinner_text = ''.join([Fore.MAGENTA, Style.BRIGHT, 'Scanning All Open Ports', Style.RESET_ALL])
    spinners = [
        Halo(text=spinner_text, spinner='dots'),
        Halo(text=spinner_text, spinner='dots2'),
        Halo(text=spinner_text, spinner='dots3'),
        Halo(text=spinner_text, spinner='dots4'),
        Halo(text=spinner_text, spinner='dots5'),
        Halo(text=spinner_text, spinner='dots6'),
        Halo(text=spinner_text, spinner='dots7'),
        Halo(text=spinner_text, spinner='dots8'),
        Halo(text=spinner_text, spinner='dots9'),
        Halo(text=spinner_text, spinner='dots10'),
        Halo(text=spinner_text, spinner='dots11'),
        Halo(text=spinner_text, spinner='dots12')
    ]
    # Start each spinner in different colors
    colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
    for index, spinner in enumerate(spinners):
        color = colors[index % len(colors)]
        spinner.text = ''.join([color, Style.BRIGHT, 'Pretty Scanning All Open PORTS', Style.RESET_ALL])
        spinner.start(text=None)  # type: ignore
    pool = multiprocessing.Pool(processes=(os.cpu_count() or 1) + 4)
    try:
        results: List[Tuple[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = pool.starmap(scan_port, [(ip, port, proto, nm) for proto, ports in open_ports.items() for port in ports])
        for port, result in results:
            print(f"Port: {port}, Result: {result}")
    except Exception as e:
        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred during scanning of all open ports on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
    finally:
        pool.close()
        pool.join()

    for spinner in spinners:
        spinner.stop()

def worker(ip: str, ports: List[int], proto: str, nm: nmap.PortScanner, spinner: Halo, completed: Dict[str, int]) -> Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = {}

    def scan_and_update(port: int, ip: str, proto: str, nm: nmap.PortScanner, spinner: Halo, completed: Dict[str, int], results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]):
        colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
        color_cycle = itertools.cycle(colors)  # Create a cycle iterator for colors
        stop_event = threading.Event()

        def update_spinner_text(base_text: str):
            while not stop_event.is_set():
                color = next(color_cycle)
                percentage = (completed['count'] / completed['total']) * 100
                spinner.text = f'\r{color}{Style.BRIGHT}{base_text} {Fore.GREEN}{Style.BRIGHT}[{Fore.MAGENTA}{Style.BRIGHT}TOTAL PORTS{Style.RESET_ALL}{Fore.CYAN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{completed["count"]}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}/{Style.RESET_ALL}{completed["total"]}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT} {Fore.YELLOW}{Style.BRIGHT}PROGRESS{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{percentage:.2f}{Fore.RED}{Style.BRIGHT}%{Style.RESET_ALL}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}'
                time.sleep(0.5)  # Update the color every 0.5 seconds
        try:
            threading.Thread(target=update_spinner_text, args=(f'Pretty Scan Starting On {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL} ',), daemon=True).start()
            port_result = scan_port(ip, port, proto, nm)
            stop_event.set()
            if port_result[1]:
                results[port_result[0]] = port_result[1]
                completed['count'] += 1
                stop_event.clear()
                threading.Thread(target=update_spinner_text, args=(f'Pretty Scan Finished On {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL} ',), daemon=True).start()
            else:
                stop_event.clear()
                threading.Thread(target=update_spinner_text, args=(f'Pretty Scan 0 Results On {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL} ',), daemon=True).start()
        except Exception as e:
            log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred during Scan and update for port{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}{port}{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}on IP{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{ip}: {e}{Style.RESET_ALL}")
        finally:
            stop_event.set()
            time.sleep(5)
            stop_event.clear()
            threading.Thread(target=update_spinner_text, args=(f'Pretty Scan Progress On {Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL} ',), daemon=True).start()
            time.sleep(15)
            stop_event.set()

    max_workers = (cpu_count() or 1) + 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(scan_and_update, ports, [ip]*len(ports), [proto]*len(ports), [nm]*len(ports), [spinner]*len(ports), [completed]*len(ports), [results]*len(ports))
    return results

def distribute_work(ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    init()
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}
    proto = None
    total_ports = sum(len(ports) for ports in open_ports.values())
    completed = {'total': total_ports, 'count': 0}

    spinner = Halo(text=f'{Fore.GREEN}{Style.BRIGHT}Initializing{Style.RESET_ALL}', spinner='dots')  # Initialize spinner here

    with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_CORES) as executor:
        futures: List[concurrent.futures.Future[Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]]] = []
        for proto, ports in open_ports.items():
            if ports:
                print(f"{Fore.CYAN}{Style.BRIGHT}Performing Detailed Scan On{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}Open Ports:{Style.RESET_ALL}")
                spinner.start(text=None)  # type: ignore
                for port in ports:
                    nm_copy = copy.deepcopy(nm)
                    futures.append(executor.submit(worker, ip, [port], proto, nm_copy, spinner, completed))
        for future in concurrent.futures.as_completed(futures):
            proto_results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = future.result()
            for port, result in proto_results.items():
                if proto is not None and result is not None:
                    detailed_results[proto][port] = result
        spinner.text = f'{Fore.GREEN}{Style.BRIGHT}Finished Scanning All Ports{Style.RESET_ALL}'
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
                        print_warning(f"{Fore.GREEN}{Style.BRIGHT}[[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}-WARNING-{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]]{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT} !POSSIBLE! VULNs ~OR~ CVEs !DETECTED!{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}[[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}-WARNING-{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]]{Style.RESET_ALL}")
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

def target_input_type(input_str: str) -> str:
    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    domain_pattern = r'^(?:[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$'
    port_pattern = r'^\d{1,5}$'
    mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    url_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w._~:/?#[\]@!$&()*+,;=]*)?$'
    asn_pattern = r'^AS\d+$'
    if re.match(ip_pattern, input_str):
        return "ip"
    elif re.match(domain_pattern, input_str):
        return "domain"
    elif re.match(port_pattern, input_str):
        return "port"
    elif re.match(mac_pattern, input_str):
        return "mac"
    elif re.match(url_pattern, input_str):
        return "url"
    elif re.match(asn_pattern, input_str):
        return "asn"
    else:
        return "unknown"

def get_target() -> Tuple[str, str]:
    init(autoreset=True)
    while True:
        print(f"{Fore.RED}{Style.BRIGHT}Enter A Scan Type{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}\n{Fore.WHITE}1.{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}LOCAL{Style.RESET_ALL}\n{Fore.WHITE}2.{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}TARGET{Style.RESET_ALL}")
        choice = input(f"{Fore.GREEN}{Style.BRIGHT}Type Choice (1 or 2): {Style.RESET_ALL}")
        if choice == "1":
            return get_local_ip(), "local"
        elif choice == "2":
            print(f"{Fore.RED}Types Include:{Style.RESET_ALL} {Fore.GREEN}[{Style.RESET_ALL}{Fore.WHITE}IP Address, Domain, Port, MAC, URL, ASN{Style.RESET_ALL}{Fore.GREEN}]{Style.RESET_ALL}")
            target = input(f"{Fore.YELLOW}{Style.BRIGHT}Enter Target Type: {Style.RESET_ALL}")
            target_type = target_input_type(target)
            if target_type == "unknown":
                log("ERROR", f"{Fore.RED}{Style.BRIGHT}Invalid input:{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}{target}{Style.RESET_ALL}")
            else:
                target = re.sub(r'^https?://', '', target)
                target = target.rstrip('/')

                spinner_text = ''.join([Fore.MAGENTA, Style.BRIGHT, 'Locating Target ', target, Style.RESET_ALL])
                spinners = [
                    Halo(text=spinner_text, spinner='dots'),
                    Halo(text=spinner_text, spinner='dots2'),
                    Halo(text=spinner_text, spinner='dots3'),
                    Halo(text=spinner_text, spinner='dots4'),
                    Halo(text=spinner_text, spinner='dots5'),
                    Halo(text=spinner_text, spinner='dots6'),
                    Halo(text=spinner_text, spinner='dots7'),
                    Halo(text=spinner_text, spinner='dots8'),
                    Halo(text=spinner_text, spinner='dots9'),
                    Halo(text=spinner_text, spinner='dots10'),
                    Halo(text=spinner_text, spinner='dots11'),
                    Halo(text=spinner_text, spinner='dots12')
                ]

                colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
                for index, spinner in enumerate(spinners):
                    color = colors[index % len(colors)]
                    spinner.text = ''.join([color, Style.BRIGHT, 'Locating Target ', target, Style.RESET_ALL])
                    spinner.start() # type: ignore

                try:
                    result = subprocess.run(f"ping -c 1 {target}", shell=True, capture_output=True, text=True)
                    for spinner in spinners:
                        spinner.stop()

                    if result.returncode == 0:
                        log("INFO", f"{Fore.GREEN}{Style.BRIGHT}Ping Check Succeeded{Style.RESET_ALL}{Fore.CYAN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}{target}{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}TARGET LOCKED{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}")
                    else:
                        log("ERROR", f"{Fore.RED}{Style.BRIGHT}Ping check failed{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}: {Fore.GREEN}{Style.BRIGHT}{target}{Style.RESET_ALL} {Fore.RED}TARGET{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}FAIL{Style.RESET_ALL}")
                except Exception as e:
                    for spinner in spinners:
                        spinner.stop()
                    log("ERROR", f"{Fore.RED}{Style.BRIGHT}ERROR RUNNING PING{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}: {e}{Style.RESET_ALL}")
                return target, target_type
        else:
            print(f"{Fore.RED}{Style.BRIGHT}Invalid choice{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.YELLOW}{Style.BRIGHT}Please enter 1 or 2.{Style.RESET_ALL}")

def main():
    target, target_type = get_target()  # Get target and target type

    if target_type == "domain":
        resolved_ip = resolve_hostname(target)
        if resolved_ip:
            target = resolved_ip
        else:
            log("ERROR", f"{Fore.RED}{Style.BRIGHT}Invalid domain: {target}{Style.RESET_ALL}")
            return

    log("INFO", f"{Fore.MAGENTA}{Style.BRIGHT}Setting Up Scan On{Style.RESET_ALL} {Fore.MAGENTA}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}{target}{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}]{Style.RESET_ALL}")
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
    nm = nmap.PortScanner()
    try:
        if target_type == "local":
            # Quick Scan for local scan
            open_ports = quick_scan(target, nm)  # Performing the quick scan and getting the open ports
            log("INFO", f"\n{Fore.GREEN}{Style.BRIGHT}Local Quick Scan Completed.{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}Identified Open Ports:{Style.RESET_ALL} \n{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['tcp']))}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['udp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}\n")  # Printing the identified open ports
        else:
            # Quick Scan for target scan
            open_ports = quick_scan(target, nm)  # Performing the quick scan and getting the open ports
            log("INFO", f"\n{Fore.GREEN}{Style.BRIGHT}Target Quick Scan Completed.{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}Identified Open Ports:{Style.RESET_ALL} \n{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['tcp']))}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{', '.join(map(str, open_ports['udp']))}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}\n") # Printing the identified open ports
    except Exception as e:
        log("ERROR", f"\n{Fore.RED}{Style.BRIGHT}Error occurred during scan: {e}{Style.RESET_ALL}")
        return

    # Detailed Scan on Open Ports
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}
    if open_ports['tcp'] or open_ports['udp']:  # Check if there are any open ports
        try:
            detailed_results = distribute_work(target, open_ports)  # Performing the distributed work on the identified open ports
        except Exception as e:
            log("ERROR", f"\n{Fore.RED}{Style.BRIGHT}Error occurred during detailed scan: {e}{Style.RESET_ALL}")
            return

    # Save scan results in parallel
    save_reports(detailed_results)

def save_reports(detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]):
    keys_to_ignore = []  # Define keys_to_ignore here
    xml_path = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_xml_report_{time.strftime('%Y%m%d%H%M%S')}.xml")
    report_filename = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_txt_report_{time.strftime('%Y%m%d%H%M%S')}.txt")
    results_json_path = os.path.join("C:\\YOUR\\FOLDER\\PATH\\GOES\\HERE", f"nmapscan_json_report_{time.strftime('%Y%m%d%H%M%S')}.json")

    # Define the save_xml_report function
    def save_xml_report():
        try:
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
                    # Create XML elements for each piece of information
                    warning_created = False
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
                        if not warning_created and ('vuln' in str(value).lower() or 'cve' in str(value).lower()):
                            warning_elem = ET.SubElement(port_elem, "Warning")
                            warning_elem.text = "[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]"
                            warning_created = True
            # Save the XML structure to the specified XML file path
            tree = ET.ElementTree(root)
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)
            log("INFO", f"\n{Fore.CYAN}{Style.BRIGHT}Detailed XML Report Saved To{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.BLUE}{Style.BRIGHT}{xml_path}{Style.RESET_ALL}\n")
        except Exception as e:
            log("ERROR", f"\n{Fore.RED}{Style.BRIGHT}Error occurred while saving the detailed XML report: {e}{Style.RESET_ALL}\n")

    # Define the save_json_report function
    def save_json_report():
        try:
            organized_results = {}
            for _, ports_info in detailed_results.items():  # Ignore the protocol
                for port, info in ports_info.items():
                    # Filter out keys with empty values
                    filtered_info = {k: v for k, v in info.items() if v}
                    if 'script' in filtered_info:
                        script_info = filtered_info['script']
                        if isinstance(script_info, dict):
                            for key, _ in script_info.items():  # Replace 'value' with underscore (_) to indicate it is intentionally unused
                                if 'vuln' in key.lower() or 'cve' in key.lower():
                                    filtered_info['warning'] = '[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]'
                                    break
                    if port not in organized_results:
                        organized_results[port] = []
                    organized_results[port].append(filtered_info)  # type: ignore # Remove the protocol from the dictionary
            with open(results_json_path, 'w') as json_file:  # Opening the JSON file in write mode
                json.dump(organized_results, json_file, indent=4)  # Writing the organized scan results to the JSON file with indentation
            log("INFO", f"\n{Fore.CYAN}{Style.BRIGHT}Detailed JSON Report Saved To{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{results_json_path}{Style.RESET_ALL}\n")
        except Exception as e:
            log("ERROR", f"\n{Fore.RED}{Style.BRIGHT}An error occurred while saving the detailed report: {str(e)}{Style.RESET_ALL}\n")

    # Define the save_text_report function
    def save_text_report():
        try:
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
                        if isinstance(script_info, dict):
                            for key, value in script_info.items():
                                if 'vuln' in key.lower() or 'cve' in key.lower():
                                    report_file.write(f"[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]\n  {key}: {value}\n")
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
                        report_file.write("\n")
            log("INFO", f"\n{Fore.CYAN}{Style.BRIGHT}Detailed TEXT Report Saved To{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.YELLOW}{Style.BRIGHT}{report_filename}{Style.RESET_ALL}\n")
        except Exception as e:
            log("ERROR", f"\n{Fore.RED}{Style.BRIGHT}Error occurred while saving the detailed TEXT report: {e}{Style.RESET_ALL}\n")

    # Use ThreadPoolExecutor to save reports in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(save_xml_report),
            executor.submit(save_text_report),
            executor.submit(save_json_report)
        ]
        for future in as_completed(futures):
            future.result()

    # Timing and final message
    elapsed_time = time.time() - start_time  # Time difference between start_time and end_time for the last scan in seconds since the last time the script was run
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    log("INFO", f"{Fore.WHITE}{Style.BRIGHT}Total process completed in{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT} {hours:02d}:{minutes:02d}:{seconds:02d}.{Style.RESET_ALL}")

if __name__ == "__main__":  # Run the script if it is executed directly
    start_time = time.time()  # Record start time of the script
    main()
