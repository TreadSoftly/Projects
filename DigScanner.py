import os
import subprocess
import shlex
from datetime import datetime

def show_help():
    print("Usage: dig_iSpy [target] [timeout] [max_retries]")
    print("")
    print("target       The target domain or IP address.")
    print("timeout      The time (in seconds) to wait for a response from dig (default: 10).")
    print("max_retries  The maximum number of retries for dig (default: 3).")

def run_tool(tool, command, output_file):
    if subprocess.getoutput(f"command -v {tool}") != '':
        with open(output_file, 'w') as file:
            subprocess.Popen(shlex.split(command), stdout=file, stderr=subprocess.DEVNULL)
    else:
        print(f"{tool} is not installed. Skipping {tool}.")

def dig_iSpy(target, timeout=10, max_retries=3):
    out_folder = f"{os.getenv('HOME')}/Desktop/DIG_LEVERAGE_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    dns_enum_json = f"{out_folder}/dns_enum.json"

    if subprocess.run(['ping', '-c', '1', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        print(f"{target} is not reachable")
        exit(1)

    os.makedirs(f"{out_folder}/dig", exist_ok=True)
    
    command = f"dig +nocmd {target} +noall +answer +dnssec -t any +bufsize=4096 +time={timeout} +retry={max_retries} -4 -6 @8.8.8.8 | sed -e '/;/d' -e 's/^[ \t]*//;s/[ \t]*$//'"
    run_tool("dig", command, f"{out_folder}/dns_enum.txt")

    print(f"DNS enumeration results are located at {dns_enum_json}.gz, {dns_enum_json}.bz2, {dns_enum_json}.xz")

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', '-?', '--?']:
        show_help()
        exit(0)

    target = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_retries = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    dig_iSpy(target, timeout, max_retries)

    # Compression of results
    for compressor in ["gzip", "bzip2", "xz"]:
        if subprocess.getoutput(f"command -v {compressor}") != '':
            subprocess.Popen([compressor, '-9', f"{dns_enum_json}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
