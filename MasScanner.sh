#!/bin/bash

# Function to display help
function show_help() {
    echo "Usage: $0 [target] [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                Show this help message and exit"
    echo "  -p, --port PORT_RANGE     Set the port range to scan (default: 0-65535)"
    echo "  -r, --rate RATE           Set the packet rate for MASSCAN (default: 10000)"
    echo "  -d, --duration DURATION   Set the scan duration (increase or decrease as needed)"
    echo "  -o, --output OUTPUT_DIR   Specify output directory for results (default: Desktop/MASSCAN_RESULTS)"
}

# Default parameters
port="0-65535"
rate=10000
duration="5m" # Adjust based on network size and scan scope
out_folder="$HOME/Desktop/MASSCAN_RESULTS_$(date +%Y-%m-%d_%H-%M-%S)"

# Parse command-line options
while getopts ":hp:r:d:o:" opt; do
    case $opt in
        h) show_help
           exit 0
           ;;
        p) port="$OPTARG"
           ;;
        r) rate="$OPTARG"
           ;;
        d) duration="$OPTARG"
           ;;
        o) out_folder="$OPTARG"
           ;;
        \?) echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :) echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# Validate target specification
if [ "$#" -ne 1 ]; then
    echo "Error: Target IP range or network is required."
    show_help
    exit 1
fi

target="$1"

# Check network reachability
if ! ping -c 1 "$target" &> /dev/null; then
    echo "Error: $target is not reachable. Check the network address and try again."
    exit 1
fi

# Ensure the output directory exists
mkdir -p "${out_folder}"

# Check if MASSCAN is installed, if not, guide for manual installation
if ! command -v masscan &> /dev/null; then
    echo "Error: Masscan is not installed. Please install Masscan before running this script."
    exit 1
fi

# Construct MASSCAN command
masscan_command="masscan -p${port} --rate=${rate} --wait=0 --duration=${duration} --output-format txt --output-filename \"${out_folder}/masscan_output.txt\" \"$target\""

# Execute MASSCAN
echo "Executing MASSCAN scan with the following parameters:"
echo "Target: $target"
echo "Port range: $port"
echo "Rate: $rate packets per second"
echo "Duration: $duration"
echo "Results will be saved to: ${out_folder}"
eval "$masscan_command"

echo "MASSCAN scan complete. Results are located at ${out_folder}/masscan_output.txt"
