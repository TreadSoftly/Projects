#!/bin/bash

function usage() {
    echo "Usage: $0 [options] <target>"
    echo ""
    echo "Options:"
    echo "  -p, --port <port>         Specify the port (default: 80)"
    echo "  -h, --help, -?, --man     Display this help message"
    echo ""
    echo "Example:"
    echo "  $0 -p 8080 example.com"
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

port=80

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -p|--port)
            port="$2"
            shift
            shift
            ;;
        -h|--help|-?|--man)
            usage
            ;;
        *)
            target="$1"
            shift
            ;;
    esac
done

if [ -z "$target" ]; then
    echo "Error: target not specified"
    exit 1
fi

if ! ping -c 1 "$target" &> /dev/null; then
    echo "$target is not reachable"
    exit 1
fi

# Create output folder
out_folder="$HOME/Desktop/LEVERAGE_$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "${out_folder}/nikto"

# Function to run a specified tool
function run_tool() {
    local tool=$1
    local command=$2
    local output_file=$3

    if command -v "$tool" &> /dev/null; then
        eval "$command" &> "${output_file}"
    else
        echo "$tool is not installed. Skipping $tool."
    fi
}

# Run Nikto scan
run_tool "nikto" 'nikto -host "$target" -port "$port" -o "${out_folder}/nikto/nikto_output.txt"'

echo "Nikto scan results are located at ${out_folder}/nikto/nikto_output.txt"
