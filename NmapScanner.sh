#!/bin/bash

function nmap_iSpy() {
    if [ "$#" -lt 1 ]; then
        echo "Error: target not specified"
        exit 1
    fi

    target=$1
    out_folder="/home/treadsoftly/Desktop/LEVERAGE_$(date +%Y-%m-%d_%H-%M-%S)"
    scan_type="${2:-"tcp,udp"}"
    port="${3:-"0-65535"}"
    verbosity="${4:-2}"
    scan_duration="${5:-"20m"}"
    scan_detail="${6:-3}"

    # Improved target reachability check with a more informative message
    if ! ping -c 1 "$target" > /dev/null 2>&1; then
        echo "Error: $target is not reachable. Please verify the target address."
        exit 1
    fi

    mkdir -p "${out_folder}/nmap"

    function run_tool() {
        local tool=$1
        local command=$2
        local output_file=$3

        if command -v "$tool" &> /dev/null; then
            echo "Running $tool scan..."
            eval "$command" &> "$output_file" &
            wait $!
            echo "$tool scan completed. Results saved to $output_file."
        else
            echo "Error: $tool is not installed. Skipping $tool scan."
        fi
    }

    # Enhanced nmap command to utilize the function's dynamic variables
    nmap_command="nmap -O -sV --script=vulners,vulscan --version-intensity 5 -p $port -vvv -T4 --reason -PE -PS22,25,80 -PA21,23,80,3389 -PU53,111,137 -PY -g 53 -A --osscan-guess --version-light --min-parallelism 10 --max-retries 1 --max-scan-delay 20 --defeat-rst-ratelimit --open -oA \"${out_folder}/nmap/nmap_scan_$target\" $target"
    run_tool "nmap" "$nmap_command" "${out_folder}/nmap/nmap_scan_${target}.txt"

    # Optimizing report file creation and compression tasks
    report_file="${out_folder}/report.txt"
    echo "Scan results have been compiled in $report_file" > "$report_file"
    echo "Final report is located at ${report_file}"

    # Streamlining compression tasks
    for extension in xml nmap gnmap; do
        if command -v bzip2 &> /dev/null; then
            bzip2 -9 "${out_folder}/nmap/nmap_scan_${target}.${extension}" &
        elif command -v gzip &> /dev/null; then
            gzip -9 "${out_folder}/nmap/nmap_scan_${target}.${extension}" &
        elif command -v xz &> /dev/null; then
            xz -9 "${out_folder}/nmap/nmap_scan_${target}.${extension}" &
        else
            echo "No compression tool available. Skipping compression."
        fi
    done

    wait
    echo "Compression of Nmap scan results completed."
    echo "Scan and compression results are located in ${out_folder}"
}

nmap_iSpy "$@"
