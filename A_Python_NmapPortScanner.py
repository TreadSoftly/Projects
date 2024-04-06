import nmap
import concurrent.futures
import os
import socket
import sys
import multiprocessing
import contextlib
from tqdm import tqdm
import time
from typing import Dict, List, Tuple, Union, Optional
import copy

# Ensure Nmap is available
try:
    nm = nmap.PortScanner()
except nmap.PortScannerError as e:
    print(f"Nmap not found: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
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

CPU_CORES = multiprocessing.cpu_count() or 1  # Ensuring at least 1 core is used
nm = nmap.PortScanner()


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    return local_ip

def quick_scan(ip: str, nm: nmap.PortScanner) -> Dict[str, List[int]]:
    print("Performing quick scan for TCP and UDP ports...")
    arguments = "-T3 --open"
    nm.scan(hosts=ip, ports="1-65535", arguments=arguments)
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
    open_ports = {'tcp': [], 'udp': []}
    for proto in nm[ip].all_protocols():
        print(f"Scanning {proto.upper()} ports...")
        for port in tqdm(sorted(nm[ip][proto].keys()), desc=f"Quick scanning {proto.upper()} ports"):
            if nm[ip][proto][port]['state'] == 'open':
                open_ports[proto].append(port)
    return open_ports

def scan_port(ip: str, port: int, proto: str, nm: nmap.PortScanner) -> Tuple[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    arguments = "-T4 -sV -sC -A -O --version-intensity 9 --script=banner,malware,vuln"
    nm.scan(hosts=ip, ports=str(port), arguments=arguments, sudo=True if proto == 'udp' else False)
    scan_info = nm[ip].get(proto, {}).get(port, {})
    result = {
        "state": scan_info.get('state', 'closed'),
        "name": scan_info.get('name', ''),
        "product": scan_info.get('product', ''),
        "version": scan_info.get('version', ''),
        "extrainfo": scan_info.get('extrainfo', ''),
        "reason": scan_info.get('reason', ''),
        "script": scan_info.get('script', {})
    }
    return port, result

def worker(ip: str, ports: List[int], proto: str, nm: nmap.PortScanner) -> Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = {}
    results = {}
    for port in tqdm(ports, desc=f"Scanning {proto.upper()} ports {ports[0]}-{ports[-1]}", leave=False):
        port_result = scan_port(ip, port, proto, nm)
        if port_result[1]:
            results[port_result[0]] = port_result[1]
    return results

def distribute_work(ip: str, open_ports: Dict[str, List[int]]) -> Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]]:
    detailed_results: Dict[str, Dict[int, Dict[str, Union[str, List[str], Dict[str, str]]]]] = {'tcp': {}, 'udp': {}}
    proto = None  # Initialize proto to a default value
    with concurrent.futures.ThreadPoolExecutor(max_workers=CPU_CORES) as executor:
        futures: List[concurrent.futures.Future[Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]]]] = []
        for proto, ports in open_ports.items():
            if ports:
                print(f"Performing detailed {proto.upper()} scan on open ports...")
                for port in ports:
                    nm_copy = copy.deepcopy(nm)  # Make a deep copy of nm for this thread
                    futures.append(executor.submit(worker, ip, [port], proto, nm_copy))

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Detailed Scanning Progress", unit="port"):
            proto_results: Dict[int, Optional[Dict[str, Union[str, List[str], Dict[str, str]]]]] = future.result()
            if proto is not None and proto not in detailed_results:
                detailed_results[proto] = {}
            for port, result in proto_results.items():
                if proto is not None and result is not None:  # Ensure result is not None before assigning it
                    detailed_results[proto][port] = result
    return detailed_results

def main():
    ip = get_local_ip()
    print(f"Scanning {ip} using optimal system resources...")
    start_time = time.time()
    open_ports: Dict[str, List[int]] = {'tcp': [], 'udp': []}
    distribute_work(ip, open_ports)  # Update open_ports in-place

    # Quick Scan
    print("\nStarting quick scan...")
    open_ports = quick_scan(ip, nm)
    print(f"Quick scan completed. Identified open ports: {open_ports}")

    # Detailed Scan on Open Ports
    detailed_results = {}
    if open_ports:
        print("\nStarting detailed scan on identified open ports...")
        detailed_results = distribute_work(ip, open_ports)
        for _, ports_info in detailed_results.items():
            for port, info in ports_info.items():
                print(f"Port {port}: {info}")

    # Output results to a file
    report_filename = os.path.join("C:\\Users\\MrDra\\OneDrive\\Desktop\\PythonTools", f"nmap_scan_report_{time.strftime('%Y%m%d%H%M%S')}.txt")
    with open(report_filename, "w") as report_file:
        for _, ports_info in detailed_results.items():
            for port, info in ports_info.items():
                if info:  # Ensure there's information to write
                    state = info.get("state", "N/A")
                    service = info.get("name", "Unknown service")
                    product = info.get("product", "")
                    version = info.get("version", "")
                    extra = info.get("extrainfo", "")
                    reason = info.get("reason", "")
                    script_info = info.get("script", {})
                    if isinstance(script_info, dict):
                        script_output = "\n".join([f"{str(k)}: {str(v)}" for k, v in script_info.items()])
                    else:
                        script_output = ""
                    report_line = f"Port {port}/TCP {state}: {service} {product} {version} {extra} {reason}\nScript Output:\n{script_output}\n\n"
                    report_file.write(report_line)
    print(f"Detailed report saved to {report_filename}")

    elapsed_time = time.time() - start_time
    print(f"\nCompleted scan in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
