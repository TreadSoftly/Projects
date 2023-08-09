#!/bin/bash

function show_help() {
    echo "Usage: $0 [target] [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message and exit"
    echo "  -p, --port PORT_RANGE   Set the port range to scan (default: 0-65535)"
    echo "  -r, --rate RATE         Set the packet rate for masscan (default: 1000)"
    echo "  -d, --duration DURATION Set the scan duration (default: 20m)"
}

while getopts ":hp:r:d:" opt; do
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
        \?) echo "Invalid option: -$OPTARG" >&2
            show_help
            exit 1
            ;;
        :) echo "Option -$OPTARG requires an argument." >&2
           show_help
           exit 1
           ;;
    esac
done
shift $((OPTIND-1))

if [ "$#" -ne 1 ]; then
    show_help
    exit 1
fi

target="$1"
out_folder="$HOME/Desktop/MASSCAN_$(date +%Y-%m-%d_%H-%M-%S)"
port="${port:-"0-65535"}"
rate="${rate:-1000}"
duration="${duration:-"20m"}"

if ! ping -c 1 "$target" &> /dev/null; then
    echo "$target is not reachable"
    exit 1
fi

mkdir -p "${out_folder}"

masscan_path="https://github.com/robertdavidgraham/masscan"

if ! command -v masscan &> /dev/null; then
    echo "Masscan is not installed. Cloning masscan from GitHub and compiling..."
    git clone "$masscan_path"
    cd masscan || exit
    make
    sudo make install
    cd ..
    rm -rf masscan
fi

masscan_command="masscan -p${port} --rate=${rate} --wait=0 --duration=${duration} --output-format txt --output-filename \"${out_folder}/masscan_output.txt\" \"${target}\""

echo "Running masscan with the following command:"
echo "$masscan_command"
eval "$masscan_command"

echo "Masscan results are located at ${out_folder}/masscan_output.txt"
