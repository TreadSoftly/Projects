# MOST OF THIS SHOULD BE AUTOMATED FROM AUTO INSTALLING MODULES NEEDED TO AUTO CREATING A ROOT FOLDER ON THE DESKTOP NAMED LEVERAGE WITH TEXT, JSON AND XML FILES ALONG WITH BROKEN DOWN DETAILED FILES
# STILL WORKING OUT SOME OF THE OFF-HAND BUGS AND TINKERING AROUND IN IT TO GET THE DNS FILES TO POPULATE FOR A VERSION 2 LATER ON FOR DEEPER SCANNING

import ast
import asyncio
import concurrent.futures
import importlib.util
import itertools
import json
import logging
import logging.config
import os
import platform
import re
import socket
import subprocess
import sys
import threading
import time
import warnings
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from itertools import cycle
from logging import LogRecord
from multiprocessing import cpu_count
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union
from urllib.parse import urlparse

import nmap
import psutil
from colorama import Fore, Style, init
from dask.distributed import Client, LocalCluster
from distributed.comm.core import CommClosedError
from halo import Halo  # type: ignore

# Suppress specific warnings
warnings.filterwarnings("ignore", message="Creating scratch directories is taking a surprisingly long time")

# Global logger variable
logger: logging.Logger

class SelectorsFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return not record.getMessage().startswith("Using selector:")

class SuppressErrorFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        unwanted_errors = [
            "Error resolving IP address for",
            "Error decoding JSON file",
            "Extracted DNS SANs:",
            "Running nikto scan on",
            "Nikto scan results saved to"
        ]
        return not any(error in record.getMessage() for error in unwanted_errors)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "WARNING",  # Change log level to WARNING to suppress lower-level messages
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["suppress_error_filter"]
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": "prettyscan.log"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True
        },
        "selectors": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "filters": ["selectors_filter"]
        }
    },
    "filters": {
        "selectors_filter": {
            "()": SelectorsFilter
        },
        "suppress_error_filter": {
            "()": SuppressErrorFilter
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def strip_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def log(level: str, message: str, console: bool = True):
    stripped_message = strip_ansi_codes(message)
    if console:
        print(message)
    logger.log(getattr(logging, level.upper(), logging.INFO), stripped_message)

class DirectoryManager:
    @staticmethod
    def get_desktop_path() -> str:
        if platform.system() == "Windows":
            try:
                import winreg as reg
                key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
                desktop_path, _ = reg.QueryValueEx(key, "Desktop")
                desktop_path = os.path.expandvars(desktop_path)
                return desktop_path
            except Exception as e:
                logger.error(f"Error retrieving Desktop path from registry: {e}")
                return os.path.join(os.path.expanduser('~'), 'Desktop')
        else:
            return os.path.join(os.path.expanduser('~'), 'Desktop')

    @staticmethod
    def create_directories() -> Tuple[str, str, str, str]:
        desktop_dir = DirectoryManager.get_desktop_path()
        base_dir = os.path.join(desktop_dir, 'LEVERAGE')
        sub_dirs = ['XML', 'TXT', 'JSON', 'PRETTY_SCAN_LOGS']
        dir_paths = [os.path.join(base_dir, sub_dir) for sub_dir in sub_dirs]
        for path in dir_paths:
            os.makedirs(path, exist_ok=True)
        return dir_paths[0], dir_paths[1], dir_paths[2], dir_paths[3]

class LoggerSetup:
    @staticmethod
    def create_log_file(log_dir: str) -> str:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = os.path.join(log_dir, f"prettyscan_log_{current_date}.log")
        if not os.path.exists(log_file):
            with open(log_file, 'a') as lf:
                lf.write(f"Log file created on {current_date}\n")
        return log_file

    @staticmethod
    def setup_logger(log_file: str) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file)
        c_handler.setLevel(logging.WARNING)  # Set console log level to WARNING
        f_handler.setLevel(logging.DEBUG)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        f_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        return logger

class ModuleInstaller:
    """Class for installing necessary modules."""

    @staticmethod
    def dynamic_worker_count() -> int:
        """Determine the optimal number of workers based on system resources."""
        total_memory = psutil.virtual_memory().total
        memory_factor = total_memory // (512 * 1024 * 1024)
        cpu_factor = psutil.cpu_count() * 3
        return min(memory_factor, cpu_factor, 61)

    @staticmethod
    def install_system_dependencies():
        """Install system dependencies like pip and nmap."""
        try:
            if platform.system() == "Windows":
                # Check and install pip
                subprocess.check_call([sys.executable, '-m', 'ensurepip', '--default-pip'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

                # Check and install nmap
                try:
                    subprocess.check_call(['nmap', '--version'])
                except subprocess.CalledProcessError:
                    log("ERROR", "Nmap not found. Please install Nmap manually.", console=True)
                    sys.exit(1)
            elif platform.system() == "Darwin":  # macOS
                # Check and install Homebrew if not installed
                try:
                    subprocess.check_call(['brew', '--version'])
                except subprocess.CalledProcessError:
                    subprocess.check_call(['/bin/bash', '-c', "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])

                # Check and install pip
                subprocess.check_call(['brew', 'install', 'python'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

                # Check and install nmap
                try:
                    subprocess.check_call(['nmap', '--version'])
                except subprocess.CalledProcessError:
                    subprocess.check_call(['brew', 'install', 'nmap'])
            else:
                # Check and install pip
                subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'python3-pip'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

                # Check and install nmap
                try:
                    subprocess.check_call(['nmap', '--version'])
                except subprocess.CalledProcessError:
                    subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'nmap'])
        except Exception as e:
            log("ERROR", f"Error installing system dependencies: {e}", console=False)
            sys.exit(1)

    @staticmethod
    async def install_module(module_name: str) -> None:
        """Install a single module."""
        if importlib.util.find_spec(module_name) is not None:
            log("INFO", f"{Fore.GREEN}{Style.BRIGHT}{module_name} is already installed.{Style.RESET_ALL}", console=False)
            return

        try:
            log("INFO", f"{Fore.YELLOW}{Style.BRIGHT}Installing {module_name}...{Style.RESET_ALL}", console=False)
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', module_name])
        except subprocess.CalledProcessError as e:
            log("ERROR", f"{Fore.RED}{Style.BRIGHT}Failed to install {module_name}. Error: {e}. Continuing...{Style.RESET_ALL}", console=False)

    @staticmethod
    async def install_modules(modules: Sequence[str]) -> None:
        """Install necessary Python modules."""
        tasks = [ModuleInstaller.install_module(module) for module in modules]
        await asyncio.gather(*tasks)

    @staticmethod
    def extract_modules_from_script(file_path: str) -> Sequence[str]:
        """Extract module names from the given Python script."""
        imported_modules: Set[str] = set()
        try:
            with open(file_path, 'r') as file:
                tree: ast.Module = ast.parse(file.read(), filename=file_path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported_modules.add(node.module)
        except IndentationError as e:
            log("ERROR", f"Indentation error in file {file_path}: {e}", console=False)
        except SyntaxError as e:
            log("ERROR", f"Syntax error in file {file_path}: {e}", console=False)
        return list(imported_modules)

    @staticmethod
    def install_modules_from_script(file_path: str):
        """Install modules extracted directly from the Python script."""
        ModuleInstaller.install_system_dependencies()
        modules = ModuleInstaller.extract_modules_from_script(file_path)
        asyncio.run(ModuleInstaller.install_modules(modules))

class NmapScanner:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.nm = self.initialize_nmap()

    @staticmethod
    def initialize_nmap() -> nmap.PortScanner:
        try:
            nm = nmap.PortScanner()
        except nmap.PortScannerError as e:
            log("ERROR", f"Nmap not found. Error: {e}. Installing 'python-nmap'...", console=True)
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-nmap'])
            nm = nmap.PortScanner()
        except Exception as e:
            log("ERROR", f"Unexpected error: {e}", console=True)
            sys.exit(1)
        return nm

    @staticmethod
    def dynamic_worker_count() -> int:
        total_memory = psutil.virtual_memory().total
        memory_factor = total_memory // (512 * 1024 * 1024)
        cpu_factor = psutil.cpu_count() * 3
        return min(memory_factor, cpu_factor, 61)

    def scan_port(self, ip: str, port: int, proto: str) -> Tuple[int, Dict[str, Union[str, List[str], Mapping[str, str]]]]:
        log("INFO", f"Scanning port {port} on IP {ip} using {proto}", console=False)

        arguments = "-sS -T4 -sV -A -O --spoof-mac Cisco --version-intensity 9 --script=default,vuln,banner,http-headers,http-title,dns-recursion,dns-srv-enum,dns-brute,broadcast-dns-service-discovery,vulscan/vulscan.nse -Pn -PE -PP -PM -PS21,23,80,3389 -PA80,443,8080 --source-port 53 -g 53 --data-length 5 -vvv"

        try:
            self.nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)
        except nmap.PortScannerError as e:
            log("ERROR", f"Error occurred while scanning port {port} on IP {ip}: {e}", console=False)
            return port, {}
        except Exception as e:
            log("ERROR", f"Unexpected error occurred while scanning port {port} on IP {ip}: {e}", console=False)
            return port, {}

        scan_info = self.nm[ip].get(proto, {}).get(port, {})
        log("DEBUG", f"Scan info for port {port} on IP {ip}: {scan_info}", console=False)
        return port, scan_info

    def quick_scan(self, ip: str) -> Dict[str, List[int]]:
        arguments = "-sS --open --spoof-mac Cisco -Pn -PE -PP -PM -PS21,23,80,3389 -PA80,443,8080 --data-length 5 -vvv"
        total_ports = 65535
        completed = {'count': 0, 'total': total_ports}
        open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
        current_port = {'port': None}

        spinner_text = 'INITIALIZING PRETTY SCAN'
        spinner = Halo(text=spinner_text, spinner='dots')
        spinner.start()  # type: ignore
        colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLACK, Fore.WHITE, Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTYELLOW_EX]
        color_cycle = itertools.cycle(colors)
        stop_event = threading.Event()

        def update_spinner_text():
            while not stop_event.is_set():
                color = next(color_cycle)
                percentage = (completed['count'] / completed['total']) * 100
                spinner.text = (
                    f'{color}{Style.BRIGHT}INITIALIZING PRETTY SCAN '
                    f'{Fore.GREEN}{Style.BRIGHT}[{Fore.WHITE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{current_port["port"]}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}] '
                    f'{Fore.GREEN}{Style.BRIGHT}[{Fore.MAGENTA}{Style.BRIGHT}PORTS SCANNED{Style.RESET_ALL}'
                    f'{Fore.CYAN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}'
                    f'{completed["count"]}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}/{Style.RESET_ALL}'
                    f'{completed["total"]}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT} '
                    f'{Fore.YELLOW}{Style.BRIGHT}PROGRESS{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}'
                    f'{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{percentage:.2f}{Fore.RED}{Style.BRIGHT}%{Style.RESET_ALL}'
                    f'{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]'
                )
                time.sleep(0.1)

        threading.Thread(target=update_spinner_text, daemon=True).start()

        def scan_callback(host: str, scan_result: nmap.PortScannerHostDict) -> None:
            for proto in scan_result.all_protocols():
                ports = scan_result[proto].keys()
                for port in ports:
                    current_port['port'] = port
                    completed['count'] += 1
                    state = scan_result[proto][port]['state']
                    if state == 'open':
                        open_ports[proto].append(port)

        try:
            self.nm.scan(hosts=ip, ports="1-65535", arguments=arguments)
            for host in self.nm.all_hosts():
                scan_callback(host, self.nm[host])
        except nmap.PortScannerError as e:
            log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred during quick scan on IP {ip}: {e}{Style.RESET_ALL}", console=False)
            stop_event.set()
            spinner.stop()
            return open_ports
        except Exception as e:
            log("ERROR", f"{Fore.RED}{Style.BRIGHT}Unexpected error occurred during quick scan on IP {ip}: {e}{Style.RESET_ALL}", console=False)
            stop_event.set()
            spinner.stop()
            return open_ports

        stop_event.set()
        spinner.stop()
        return open_ports

def extract_dns_san(cert_text: str) -> List[str]:
    dns_san_pattern = re.compile(r'DNS:([a-zA-Z0-9.-]+)')
    dns_san_matches = dns_san_pattern.findall(cert_text)
    log("DEBUG", f"Extracted DNS SANs: {dns_san_matches}", console=False)
    return dns_san_matches

def process_txt_files(txt_dir: str) -> List[str]:
    dns_san_entries: List[str] = []
    for root, _, files in os.walk(txt_dir):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    dns_san_entries.extend(extract_dns_san(content))
    return dns_san_entries

def process_json_files(json_dir: str) -> List[str]:
    dns_san_entries: List[str] = []
    for root, _, files in os.walk(json_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                        if isinstance(content, dict) or isinstance(content, list):
                            content = json.dumps(content)
                        dns_san_entries.extend(extract_dns_san(content))
                except (json.JSONDecodeError, Exception):
                    continue  # Skip the file if there's an error
    return dns_san_entries

def process_xml_files(xml_dir: str) -> List[str]:
    dns_san_entries: List[str] = []
    for root, _, files in os.walk(xml_dir):
        for file in files:
            if file.endswith(".xml"):
                tree = ET.parse(os.path.join(root, file))
                root_elem = tree.getroot()
                content: str = ET.tostring(root_elem, encoding='utf-8', method='text').decode('utf-8')
                dns_san_entries.extend(extract_dns_san(content))
    return dns_san_entries

def save_dns_san_to_file(dns_san_entries: List[str], output_file: str):
    unique_entries = list(set(dns_san_entries))
    with open(output_file, 'w') as f:
        for entry in unique_entries:
            f.write(f"{entry}\n")

def save_dns_san_to_json(dns_san_entries: List[str], output_file: str):
    unique_entries = list(set(dns_san_entries))
    with open(output_file, 'w') as f:
        json.dump(unique_entries, f, indent=4)

def save_dns_san_to_xml(dns_san_entries: List[str], output_file: str):
    unique_entries = list(set(dns_san_entries))
    root = ET.Element("DNS_SANs")
    for entry in unique_entries:
        dns_san_elem = ET.SubElement(root, "DNS_SAN")
        dns_san_elem.text = entry
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

class ReportGenerator:
    def __init__(self, xml_dir: str, txt_dir: str, json_dir: str, logger: logging.Logger):
        self.xml_dir = xml_dir
        self.txt_dir = txt_dir
        self.json_dir = json_dir
        self.logger = logger

    def save_reports(self, detailed_results: Mapping[str, Mapping[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]], tag: str):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        xml_path = os.path.join(self.xml_dir, f"nmapscan_xml_report_{tag}_{timestamp}.xml")
        report_filename = os.path.join(self.txt_dir, f"nmapscan_txt_report_{tag}_{timestamp}.txt")
        results_json_path = os.path.join(self.json_dir, f"nmapscan_json_report_{tag}_{timestamp}.json")

        detailed_xml_dir = os.path.join(self.xml_dir, "detailed")
        detailed_txt_dir = os.path.join(self.txt_dir, "detailed")
        detailed_json_dir = os.path.join(self.json_dir, "detailed")

        os.makedirs(detailed_xml_dir, exist_ok=True)
        os.makedirs(detailed_txt_dir, exist_ok=True)
        os.makedirs(detailed_json_dir, exist_ok=True)

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.save_xml_report, detailed_results, xml_path, detailed_xml_dir),
                executor.submit(self.save_text_report, detailed_results, report_filename, detailed_txt_dir),
                executor.submit(self.save_json_report, detailed_results, results_json_path, detailed_json_dir)
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                    self.logger.info(f"Report saved successfully.")
                except Exception as e:
                    self.logger.error(f"Error occurred while saving report: {e}")

        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        total_ports = sum(len(ports) for ports in detailed_results.values())
        self.logger.info(f"TOTAL OPEN PORTS SCANNED: {total_ports}")
        self.logger.info(f"Report generation completed in {hours:02d}:{minutes:02d}:{seconds:02d}.")

    @staticmethod
    def save_detailed_file(detailed_dir: str, field: str, value: Union[str, List[str], Mapping[str, str]], file_format: str) -> None:
        os.makedirs(detailed_dir, exist_ok=True)
        if file_format == "txt":
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    ReportGenerator.save_detailed_file(detailed_dir, f"{field}_{sub_key}", sub_value, file_format)
            elif isinstance(value, list):
                with open(os.path.join(detailed_dir, f"{field}.txt"), "a") as file:
                    for item in value:
                        file.write(f"{strip_ansi_codes(str(item))}\n")
            else:
                with open(os.path.join(detailed_dir, f"{field}.txt"), "a") as file:
                    file.write(f"{strip_ansi_codes(str(value))}\n")
        elif file_format == "json":
            detailed_file_path = os.path.join(detailed_dir, f"{field}.json")
            if isinstance(value, dict):
                with open(detailed_file_path, "a") as file:
                    json.dump(value, file, indent=4)
            elif isinstance(value, list):
                with open(detailed_file_path, "a") as file:
                    json.dump(value, file, indent=4)
            else:
                with open(detailed_file_path, "a") as file:
                    json.dump({field: value}, file, indent=4)
        elif file_format == "xml":
            detailed_file_path = os.path.join(detailed_dir, f"{field}.xml")
            root = ET.Element(field)
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    sub_elem = ET.SubElement(root, sub_key)
                    sub_elem.text = strip_ansi_codes(str(sub_value))
            elif isinstance(value, list):
                for item in value:
                    item_elem = ET.SubElement(root, field)
                    item_elem.text = strip_ansi_codes(str(item))
            else:
                root.text = strip_ansi_codes(str(value))
            tree = ET.ElementTree(root)
            tree.write(detailed_file_path, encoding='utf-8', xml_declaration=True)

    def save_xml_report(self, detailed_results: Mapping[str, Mapping[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]], xml_path: str, detailed_dir: str):
        try:
            os.makedirs(os.path.dirname(xml_path), exist_ok=True)
            root = ET.Element("NmapScanResults")

            for ip, ports_info in detailed_results.items():
                ip_elem = ET.SubElement(root, "IP")
                ip_elem.set("address", ip)
                for port, info in ports_info.items():
                    port_elem = ET.SubElement(ip_elem, "Port")
                    port_elem.set("id", str(port))
                    filtered_info = {k: v for k, v in info.items() if v and v not in ['Not available', 'None']}

                    vulnerability_found = False
                    vulnerability_details: List[str] = []

                    for key, value in filtered_info.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subvalue and subvalue not in ['Not available', 'None']:
                                    if 'vuln' in subkey.lower() or 'cve' in subkey.lower() or 'exploit' in subkey.lower():
                                        vulnerability_found = True
                                        vulnerability_details.append(f"{key + subkey.replace('_', '').capitalize()}: {strip_ansi_codes(str(subvalue))}")
                                    elif 'dns' in subkey.lower() or 'subject alternative name' in subkey.lower():
                                        dns_sans = extract_dns_san(subvalue)
                                        for dns_san in dns_sans:
                                            self.save_detailed_file(detailed_dir, "dns", dns_san, "xml")
                                    else:
                                        sub_elem = ET.SubElement(port_elem, key + subkey.replace('_', '').capitalize())
                                        sub_elem.text = strip_ansi_codes(str(subvalue))
                                    self.save_detailed_file(detailed_dir, f"{key}_{subkey}", subvalue, "xml")
                        elif isinstance(value, list):
                            for item in value:
                                if 'vuln' in str(item).lower() or 'cve' in str(item).lower() or 'exploit' in str(item).lower():
                                    vulnerability_found = True
                                    vulnerability_details.append(f"{key.replace('_', '').capitalize()}: {strip_ansi_codes(str(item))}")
                                elif 'dns' in str(item).lower() or 'subject alternative name' in str(item).lower():
                                    dns_sans = extract_dns_san(item)
                                    for dns_san in dns_sans:
                                        self.save_detailed_file(detailed_dir, "dns", dns_san, "xml")
                                else:
                                    list_elem = ET.SubElement(port_elem, key.replace('_', '').capitalize())
                                    list_elem.text = strip_ansi_codes(str(item))
                                self.save_detailed_file(detailed_dir, key, item, "xml")
                        else:
                            if 'vuln' in str(value).lower() or 'cve' in str(value).lower() or 'exploit' in str(value).lower():
                                vulnerability_found = True
                                vulnerability_details.append(f"{key.replace('_', '').capitalize()}: {strip_ansi_codes(str(value))}")
                            elif 'dns' in str(value).lower() or 'subject alternative name' in str(value).lower():
                                dns_sans = extract_dns_san(str(value))
                                for dns_san in dns_sans:
                                    self.save_detailed_file(detailed_dir, "dns", dns_san, "xml")
                            else:
                                info_elem = ET.SubElement(port_elem, key.replace('_', '').capitalize())
                                info_elem.text = strip_ansi_codes(str(value))
                            self.save_detailed_file(detailed_dir, key, value, "xml")

                        if vulnerability_found:
                            warning_elem = ET.SubElement(port_elem, "Warning")
                            warning_elem.text = "[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]"
                            for detail in vulnerability_details:
                                tag, detail_text = detail.split(": ", 1)
                                detail_elem = ET.SubElement(port_elem, tag)
                                detail_elem.text = detail_text

                tree = ET.ElementTree(root)
                tree.write(xml_path, encoding='utf-8', xml_declaration=True)
                self.logger.info(f"Detailed XML Report Saved To {xml_path}")
        except Exception as e:
            self.logger.error(f"Error occurred while saving the detailed XML report: {e}")

    def save_json_report(self, detailed_results: Mapping[str, Mapping[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]], results_json_path: str, detailed_dir: str):
        try:
            os.makedirs(os.path.dirname(results_json_path), exist_ok=True)
            organized_results: Dict[str, List[Dict[str, Union[str, List[str], Mapping[str, str]]]]] = {}

            for ip, ports_info in detailed_results.items():
                if ip not in organized_results:
                    organized_results[ip] = []
                for port, info in ports_info.items():
                    port_info: Dict[str, Union[str, List[str], Mapping[str, str]]] = {"Port": str(port)}
                    filtered_info = {k: v for k, v in info.items() if v}

                    for key, value in filtered_info.items():
                        warning_inserted = False  # Track if warning has been inserted

                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subvalue and subvalue not in ['Not available', 'None']:
                                    if ('vuln' in subkey.lower() or 'cve' in subkey.lower() or 'exploit' in subkey.lower()) and not warning_inserted:
                                        warning = f"[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]"
                                        port_info[f"Warning_{key}_{subkey}"] = warning
                                        warning_inserted = True
                                    elif 'dns' in subkey.lower() or 'subject alternative name' in subkey.lower():
                                        dns_sans = extract_dns_san(subvalue)
                                        for dns_san in dns_sans:
                                            self.save_detailed_file(detailed_dir, "dns", dns_san, "json")
                                    port_info[f"{key}_{subkey}"] = strip_ansi_codes(str(subvalue))
                                    self.save_detailed_file(detailed_dir, f"{key}_{subkey}", subvalue, "json")
                        elif isinstance(value, list):
                            processed_list: List[str] = []
                            for item in value:
                                if ('vuln' in item.lower() or 'cve' in item.lower() or 'exploit' in item.lower()) and not warning_inserted:
                                    warning = f"[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]"
                                    port_info[f"Warning_{key}"] = warning
                                    warning_inserted = True
                                elif 'dns' in item.lower() or 'subject alternative name' in item.lower():
                                    dns_sans = extract_dns_san(item)
                                    for dns_san in dns_sans:
                                        self.save_detailed_file(detailed_dir, "dns", dns_san, "json")
                                processed_list.append(strip_ansi_codes(str(item)))
                                self.save_detailed_file(detailed_dir, key, item, "json")
                            port_info[key] = processed_list
                        else:
                            if ('vuln' in str(value).lower() or 'cve' in str(value).lower() or 'exploit' in str(value).lower()) and not warning_inserted:
                                warning = f"[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]"
                                port_info[f"Warning_{key}"] = warning
                                warning_inserted = True
                            elif 'dns' in str(value).lower() or 'subject alternative name' in str(value).lower():
                                dns_sans = extract_dns_san(str(value))
                                for dns_san in dns_sans:
                                    self.save_detailed_file(detailed_dir, "dns", dns_san, "json")
                            port_info[key] = strip_ansi_codes(str(value))
                            self.save_detailed_file(detailed_dir, key, value, "json")

                        organized_results[ip].append(port_info)

            with open(results_json_path, 'w') as json_file:
                json.dump(organized_results, json_file, indent=4)
            self.logger.info(f"Detailed JSON Report Saved To {results_json_path}")
        except Exception as e:
            self.logger.error(f"An error occurred while saving the detailed report: {str(e)}")

    def save_text_report(self, detailed_results: Mapping[str, Mapping[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]], report_filename: str, detailed_dir: str):
        try:
            os.makedirs(os.path.dirname(report_filename), exist_ok=True)
            dns_san_filename = os.path.join(detailed_dir, "dns.txt")

            with open(report_filename, "w") as report_file, open(dns_san_filename, "w") as dns_san_file:
                for ip, ports_info in detailed_results.items():
                    report_file.write(f"IP: {ip}\n")
                    for port, info in ports_info.items():
                        report_file.write(f"  Port {port}:\n")
                        processed_fields: Set[str] = set()
                        vulnerability_found = False
                        vulnerability_details: List[str] = []

                        for field, value in info.items():
                            if field not in processed_fields and value and value not in ['Not available', 'None']:
                                processed_fields.add(field)
                                if isinstance(value, dict):
                                    report_file.write(f"    {field.capitalize()}:\n")
                                    for sub_key, sub_value in value.items():
                                        if sub_value and sub_value not in ['Not available', 'None']:
                                            if 'vuln' in sub_key.lower() or 'cve' in sub_key.lower() or 'exploit' in sub_key.lower():
                                                vulnerability_found = True
                                                vulnerability_details.append(f"      {sub_key}: {strip_ansi_codes(str(sub_value))}\n")
                                                self.save_detailed_file(detailed_dir, f"{field}_{sub_key}", sub_value, "txt")
                                            elif 'dns' in sub_key.lower() or 'subject alternative name' in sub_key.lower():
                                                dns_sans = extract_dns_san(sub_value)
                                                for dns_san in dns_sans:
                                                    dns_san_file.write(f"{dns_san}\n")
                                                    self.save_detailed_file(detailed_dir, "dns", dns_san, "txt")
                                            else:
                                                report_file.write(f"      {sub_key}: {strip_ansi_codes(str(sub_value))}\n")
                                                self.save_detailed_file(detailed_dir, f"{field}_{sub_key}", sub_value, "txt")
                                elif isinstance(value, list):
                                    report_file.write(f"    {field.capitalize()}:\n")
                                    for item in value:
                                        if 'vuln' in item.lower() or 'cve' in item.lower() or 'exploit' in item.lower():
                                            vulnerability_found = True
                                            vulnerability_details.append(f"      {strip_ansi_codes(item)}\n")
                                            self.save_detailed_file(detailed_dir, field, item, "txt")
                                        elif 'dns' in item.lower() or 'subject alternative name' in item.lower():
                                            dns_sans = extract_dns_san(item)
                                            for dns_san in dns_sans:
                                                dns_san_file.write(f"{dns_san}\n")
                                                self.save_detailed_file(detailed_dir, "dns", dns_san, "txt")
                                        else:
                                            report_file.write(f"      {strip_ansi_codes(item)}\n")
                                            self.save_detailed_file(detailed_dir, field, item, "txt")
                                else:
                                    if 'vuln' in str(value).lower() or 'cve' in str(value).lower() or 'exploit' in str(value).lower():
                                        vulnerability_found = True
                                        vulnerability_details.append(f"    {field.capitalize()}: {strip_ansi_codes(str(value))}\n")
                                        self.save_detailed_file(detailed_dir, field, value, "txt")
                                    elif 'dns' in str(value).lower() or 'subject alternative name' in str(value).lower():
                                        dns_sans = extract_dns_san(str(value))
                                        for dns_san in dns_sans:
                                            dns_san_file.write(f"{dns_san}\n")
                                            self.save_detailed_file(detailed_dir, "dns", dns_san, "txt")
                                    else:
                                        report_file.write(f"    {field.capitalize()}: {strip_ansi_codes(str(value))}\n")
                                        self.save_detailed_file(detailed_dir, field, value, "txt")

                                    if vulnerability_found:
                                        report_file.write(f"[[-WARNING-]] !POSSIBLE! VULNs ~OR~ CVEs !DETECTED! [[-WARNING-]]\n")
                                        for detail in vulnerability_details:
                                            report_file.write(detail)
                        report_file.write("\n")
            self.logger.info(f"Detailed TEXT Report Saved To {report_filename}")
        except Exception as e:
            self.logger.error(f"Error occurred while saving the detailed TEXT report: {e}")

class PrettyScan:
    def __init__(self):
        self.xml_dir, self.txt_dir, self.json_dir, self.log_dir = DirectoryManager.create_directories()
        self.log_file = LoggerSetup.create_log_file(self.log_dir)
        self.logger = LoggerSetup.setup_logger(self.log_file)
        global logger
        logger = self.logger
        self.logger.setLevel(logging.WARNING)
        self.nmap_scanner = NmapScanner(self.logger)
        self.report_generator = ReportGenerator(self.xml_dir, self.txt_dir, self.json_dir, self.logger)

    @staticmethod
    def format_ports(ports: List[int], per_line: int = 10) -> str:
        sorted_ports = sorted(ports)  # Sort the ports in ascending order
        lines = [sorted_ports[i:i + per_line] for i in range(0, len(sorted_ports), per_line)]
        formatted_lines = '\n'.join(
            f"{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}" +
            f"{Fore.WHITE}{Style.BRIGHT}] [{Style.RESET_ALL}".join(
                f"{Fore.RED}{Style.BRIGHT}{port:>5}{Style.RESET_ALL}" for port in line
            ) + f"{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}"
            for line in lines
        )
        return formatted_lines

    @staticmethod
    def dynamic_worker_count() -> int:
        total_memory = psutil.virtual_memory().total
        memory_factor = total_memory // (512 * 1024 * 1024)
        cpu_factor = cpu_count() * 3
        return min(memory_factor, cpu_factor, 61)

    def get_target(self) -> Tuple[str, str]:
        init(autoreset=True)
        while True:
            print(f"{Fore.RED}{Style.BRIGHT}Enter A Scan Type{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}\n{Fore.WHITE}1.{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}LOCAL{Style.RESET_ALL}\n{Fore.WHITE}2.{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}TARGET{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}Type Choice{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}({Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}1{Style.RESET_ALL} {Fore.BLACK}{Style.BRIGHT}or{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}2{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}){Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} ", end='')
            choice = input(f"{Fore.MAGENTA}{Style.BRIGHT}")
            if choice == "1":
                return self.get_local_ip(), "local"
            elif choice == "2":
                print(f"{Fore.RED}Types Include:{Style.RESET_ALL} {Fore.GREEN}[{Style.RESET_ALL}{Fore.WHITE}IP Address (e.g., 192.168.0.1), Domain (e.g., example.com), Port (e.g., 80), MAC (e.g., 00:1A:2B:3C:4D:5E), URL (e.g., https://example.com), ASN (e.g., AS12345){Style.RESET_ALL}{Fore.GREEN}]{Style.RESET_ALL}")
                target = input(f"{Fore.YELLOW}{Style.BRIGHT}Enter Target Type: {Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}")
                target_type = self.target_input_type(target)
                if target_type == "unknown":
                    print(f"{Fore.RED}{Style.BRIGHT}Invalid input:{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}{target}{Style.RESET_ALL}")
                else:
                    if target_type in ["domain", "url"]:
                        target_ip = self.get_ip_from_url(target)
                        if not target_ip:
                            print(f"{Fore.RED}Failed to resolve {target} to an IP address. Please try again.")
                            continue
                        target = target_ip
                    spinner_text = ''.join([Fore.MAGENTA, Style.BRIGHT, 'Locating Target ', target, Style.RESET_ALL])
                    spinner = Halo(text=spinner_text, spinner='dots')
                    spinner.start()  # type: ignore
                    try:
                        result = subprocess.run(f"ping -c 1 {target}", shell=True, capture_output=True, text=True)
                        spinner.stop()
                        if result.returncode == 0:
                            log("INFO", f"{Fore.GREEN}{Style.BRIGHT}Ping Check Succeeded{Style.RESET_ALL}{Fore.CYAN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}{target}{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}TARGET LOCKED{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
                        else:
                            log("INFO", f"{Fore.RED}{Style.BRIGHT}Ping check failed{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}: {Fore.GREEN}{Style.BRIGHT}{target}{Style.RESET_ALL} {Fore.RED}TARGET{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}FAIL{Style.RESET_ALL}", console=True)
                    except Exception as e:
                        spinner.stop()
                        log("ERROR", f"{Fore.RED}{Style.BRIGHT}ERROR RUNNING PING{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}: {e}{Style.RESET_ALL}", console=True)
                    return target, target_type
            else:
                print(f"{Fore.RED}{Style.BRIGHT}Invalid choice{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.YELLOW}{Style.BRIGHT}Please enter {Fore.GREEN}{Style.BRIGHT}({Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}1{Style.RESET_ALL} {Fore.BLACK}{Style.BRIGHT}or{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}2{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}){Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} ", end='')
                choice = input(f"{Fore.MAGENTA}{Style.BRIGHT}")

    @staticmethod
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

    def get_ip_from_url(self, url: str) -> Optional[str]:
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname if parsed_url.hostname else url
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except socket.gaierror:
            log("ERROR", f"Could not resolve IP address for {url}", console=False)
            return None
        except Exception as e:
            log("ERROR", f"Error resolving IP address for {url}: {e}", console=False)
            return None

    @staticmethod
    def get_local_ip() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('10.255.255.255', 1))
                local_ip = s.getsockname()[0]
        except Exception as e:
            log("ERROR", f"Failed to obtain local IP, defaulting to localhost: {e}")
            local_ip = '127.0.0.1'
        return local_ip

    def distribute_work(self, ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]]:
        init()
        detailed_results: Dict[str, Dict[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]] = {'tcp': {}, 'udp': {}}
        total_ports = sum(len(ports) for ports in open_ports.values())
        completed = {'total': total_ports, 'count': 0}
        current_port: Dict[str, Optional[int]] = {'port': None}

        spinner_text = ''.join([Fore.MAGENTA, Style.BRIGHT, 'PRETTY DEEP SCAN ON', Style.RESET_ALL])
        spinner = Halo(text=spinner_text, spinner='dots')
        colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLACK, Fore.WHITE, Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTYELLOW_EX]
        color_cycle = cycle(colors)
        stop_event = threading.Event()

        def update_spinner():
            while not stop_event.is_set():
                color = next(color_cycle)
                percentage = (completed['count'] / completed['total']) * 100
                spinner.text = (
                    f'{color}{Style.BRIGHT}PRETTY DEEP SCAN ON '
                    f'{Fore.GREEN}{Style.BRIGHT}[{Fore.WHITE}{Style.BRIGHT}Port{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{current_port["port"]}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}] '
                    f'{Fore.GREEN}{Style.BRIGHT}[{Fore.MAGENTA}{Style.BRIGHT}PORTS SCANNED{Style.RESET_ALL}'
                    f'{Fore.CYAN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}'
                    f'{completed["count"]}{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}/{Style.RESET_ALL}'
                    f'{completed["total"]}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT} '
                    f'{Fore.YELLOW}{Style.BRIGHT}PROGRESS{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}'
                    f'{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{percentage:.2f}{Fore.RED}{Style.BRIGHT}%{Style.RESET_ALL}'
                    f'{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]'
                )
                time.sleep(0.1)

        threading.Thread(target=update_spinner, daemon=True).start()

        with ThreadPoolExecutor(max_workers=self.dynamic_worker_count()) as executor:
            futures: Dict[int, concurrent.futures.Future[Dict[int, Optional[Mapping[str, Union[str, List[str], Mapping[str, str]]]]]]] = {}
            proto_results_mapping: Dict[str, List[concurrent.futures.Future[Dict[int, Optional[Mapping[str, Union[str, List[str], Mapping[str, str]]]]]]]] = {
                'tcp': [],
                'udp': []
            }
            for proto, ports in open_ports.items():
                if ports:
                    log("INFO", f"{Fore.CYAN}{Style.BRIGHT}Performing Detailed Scan On{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}OPEN PORTS{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{total_ports}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
                    spinner.start()  # type: ignore
                    for port in ports:
                        future = executor.submit(self.worker, ip, port, proto)
                        futures[port] = future
                        proto_results_mapping[proto].append(future)

            for proto, future_list in proto_results_mapping.items():
                for future in as_completed(future_list):
                    port = next((port for port, f in futures.items() if f == future), None)
                    if port is not None:
                        current_port['port'] = port
                    proto_results = future.result()
                    for port, result in proto_results.items():
                        if result is not None:
                            detailed_results[proto][port] = result
                        completed['count'] += 1

        stop_event.set()
        spinner.stop()

        logged_ports: Set[int] = set()
        logged_warnings: Set[str] = set()
        for ports_info in detailed_results.values():
            for port, info in ports_info.items():
                if port not in logged_ports:
                    if info:
                        log("", f"\n{Fore.BLUE}{Style.BRIGHT}OPEN PORT{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}~{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{port}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
                    fields = ['state', 'name', 'product', 'version', 'address', 'machine', 'memory', 'mac', 'mac_vendor', 'device', 'network', 'extrainfo', 'reason', 'osclass', 'osmatch', 'osfamily', 'hostname', 'hostnames', 'hostname_type', 'ipv4', 'ipv6', 'ipv4-id', 'ipv6 id', 'osgen', 'osaccuracy', 'osmatch', 'vlan id', 'vlan name', 'distance', 'tcp_sequence', 'tcp_options', 'service_info']
                    for field in fields:
                        if field in info and info[field] not in ['', 'Not available', 'None']:
                            if field == 'state':
                                log("INFO", f"{Fore.GREEN}{Style.BRIGHT}State{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{info['state']}{Style.RESET_ALL}", console=True)
                            elif field == 'name':
                                log("INFO", f"{Fore.BLUE}{Style.BRIGHT}Name{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}{info['name']}{Style.RESET_ALL}", console=True)
                            elif field == 'product':
                                log("INFO", f"{Fore.BLUE}{Style.BRIGHT}Product{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{info['product']}{Style.RESET_ALL}", console=True)
                            else:
                                log("INFO", f"{Fore.BLUE}{field.capitalize()}{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{info[field]}{Style.RESET_ALL}", console=True)
                    log("INFO", f"{Fore.YELLOW}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.BLUE}{Style.BRIGHT}~NMAP SCRIPTS OUTPUT BELOW IF FOUND~{Style.RESET_ALL}{Fore.YELLOW}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
                    script_info = info.get('script', {})
                    logged_warnings: Set[str] = set()
                    if isinstance(script_info, dict):
                        for key, value in script_info.items():
                            if 'vuln' in key.lower() or 'cve' in key.lower():
                                if key not in logged_warnings:
                                    print(f"{Fore.GREEN}{Style.BRIGHT}[[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}-WARNING-{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]]{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT} !POSSIBLE! VULNs{Style.RESET_ALL} {Fore.MAGENTA}{Style.BRIGHT}~OR~{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT} CVEs !DETECTED!{Style.RESET_ALL} {Fore.GREEN}{Style.BRIGHT}[[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}-WARNING-{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}]]{Style.RESET_ALL}")
                                    logged_warnings.add(key)
                                print(f"{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{key}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}vvvv=====>{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}<=====^^^^{Style.RESET_ALL}")
                            elif 'certificate' in key.lower():
                                self.print_certificate(value)
                                log("INFO", f"{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{key}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{value}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
                            else:
                                log("INFO", f"{Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.YELLOW}{Style.BRIGHT}{key}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.RED}{value}{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
                    else:
                        log("ERROR", f"{Fore.RED}{Style.BRIGHT}No script output{Style.RESET_ALL}", console=True)
                    logged_ports.add(port)

        return detailed_results

    def worker(self, ip: str, port: int, proto: str) -> Dict[int, Optional[Mapping[str, Union[str, List[str], Mapping[str, str]]]]]:
        results: Dict[int, Optional[Mapping[str, Union[str, List[str], Mapping[str, str]]]]] = {}
        nm = nmap.PortScanner()

        def scan_and_update(port: int, ip: str, proto: str, nm: nmap.PortScanner, results: Dict[int, Optional[Mapping[str, Union[str, List[str], Mapping[str, str]]]]]):
            try:
                port_result = self.nmap_scanner.scan_port(ip, port, proto)
                if port_result[1]:
                    results[port_result[0]] = port_result[1]
            except Exception as e:
                log("ERROR", f"Error occurred during PRETTY DEEP SCAN and update for port {port} on IP {ip}: {e}")

        with ThreadPoolExecutor(max_workers=self.dynamic_worker_count()) as executor:
            executor.map(scan_and_update, [port], [ip], [proto], [nm], [results])
        return results

    @staticmethod
    def print_warning(message: str):
        print(f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}")

    @staticmethod
    def print_certificate(cert_text: str):
        cert_lines = cert_text.split('\n')
        for line in cert_lines:
            if "BEGIN CERTIFICATE" in line or "END CERTIFICATE" in line:
                log("INFO", f"{Fore.YELLOW}{Style.BRIGHT}{line}{Style.RESET_ALL}")
            else:
                log("INFO", f"{Fore.CYAN}{line}{Style.RESET_ALL}")

    def main(self):
        start_time = time.time()
        target, _ = self.get_target()
        tag = target.replace('.', '_')
        log("INFO", f"{Fore.MAGENTA}{Style.BRIGHT}Setting Up Scan On{Style.RESET_ALL} {Fore.MAGENTA}{Style.BRIGHT}[{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}{target}{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)
        open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
        try:
            open_ports = self.nmap_scanner.quick_scan(target)
            log("INFO", f"{Fore.GREEN}{Style.BRIGHT}Quick Scan Completed.{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}Identified{Style.RESET_ALL} {Fore.RED}{Style.BRIGHT}OPEN PORTS{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}:{Style.RESET_ALL}")
            if open_ports['tcp']:
                formatted_tcp_ports = self.format_ports(open_ports['tcp'])
                log("INFO", f"{Fore.GREEN}{Style.BRIGHT}\n{formatted_tcp_ports}{Style.RESET_ALL}", console=True)
            if open_ports['udp']:
                formatted_udp_ports = self.format_ports(open_ports['udp'])
                log("INFO", f"{Fore.GREEN}{Style.BRIGHT}\n{formatted_udp_ports}{Style.RESET_ALL}", console=True)
        except Exception as e:
            log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred during scan: {e}{Style.RESET_ALL}", console=False)
            return
        detailed_results: Dict[str, Dict[int, Mapping[str, Union[str, List[str], Mapping[str, str]]]]] = {'tcp': {}, 'udp': {}}
        if open_ports['tcp'] or open_ports['udp']:
            try:
                detailed_results = self.distribute_work(target, open_ports)
            except Exception as e:
                log("ERROR", f"{Fore.RED}{Style.BRIGHT}Error occurred during detailed scan: {e}{Style.RESET_ALL}", console=False)
                return
        self.report_generator.save_reports(detailed_results, tag)
        self.run_nikto_scan(target)

        # Process SSL cert files and save DNS SAN entries to file
        dns_san_entries = process_txt_files(self.txt_dir)
        dns_san_entries.extend(process_json_files(self.json_dir))
        dns_san_entries.extend(process_xml_files(self.xml_dir))
        detailed_dns_txt = os.path.join(self.txt_dir, "detailed", "dns.txt")
        detailed_dns_json = os.path.join(self.json_dir, "detailed", "dns.json")
        detailed_dns_xml = os.path.join(self.xml_dir, "detailed", "dns.xml")
        save_dns_san_to_file(dns_san_entries, detailed_dns_txt)
        save_dns_san_to_json(dns_san_entries, detailed_dns_json)
        save_dns_san_to_xml(dns_san_entries, detailed_dns_xml)

        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        log("INFO", f"{Fore.WHITE}{Style.BRIGHT}TOTAL SCAN COMPLETED IN{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}{Fore.MAGENTA}{Style.BRIGHT}[{Style.RESET_ALL}{hours:02d}:{minutes:02d}:{seconds:02d}{Style.RESET_ALL}{Fore.MAGENTA}{Style.BRIGHT}]{Style.RESET_ALL}", console=True)

    def run_nikto_scan(self, url: str):
        ip_address = self.get_ip_from_url(url)
        if ip_address:
            nikto_command = f"""
            nikto -h {url} \
            -Tuning 1234567890ab \
            -timeout 5 \
            -maxtime 30m \
            -nointeractive \
            -nossl \
            -Cgidirs /cgi-bin/ \
            -Display V \
            -vhost fs.ncaa.org \
            -useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
            -mutate 123456 \
            -evasion 1 \
            -Plugins ALL \
            -output {self.txt_dir}/detailed/nikto_{ip_address}.txt -Format txt
            """
            subprocess.run(nikto_command, shell=True)
        else:
            log("ERROR", f"Could not resolve IP address for {url}")

if __name__ == "__main__":
    try:
        cluster = LocalCluster(n_workers=4, threads_per_worker=2, processes=True, silence_logs=logging.ERROR)
        client = Client(cluster)
    except CommClosedError as e:
        log("ERROR", f"Dask communication error: {e}")
        sys.exit(1)
    pretty_scan = PrettyScan()
    pretty_scan.main()
