 #!/bin/bash

function iSpy() {
    if [ "$#" -lt 1 ]; then
        echo "Error: target not specified"
        exit 1
    fi

    target=$1
    out_folder="home/treadsoflty/Desktop/LEVERAGE_$(date +%Y-%m-%d_%H-%M-%S)"
    scan_type="${2:-"tcp,udp"}"
    port="${3:-"0-65535"}"
    verbosity="${4:-2}"
    scan_duration="${5:-"20m"}"
    scan_detail="${6:-3}"

    if ! ping -c 1 "$target" &> /dev/null; then
        echo "$target is not reachable"
        exit 1
    fi

    mkdir -p "${out_folder}/nmap"

    function run_tool() {
        local tool=$1
        local command=$2
        local output_file=$3

        if command -v "$tool" &> /dev/null; then
            (eval "$command" &> "${output_file}") &
        else
            echo "$tool is not installed. Skipping $tool."
        fi
    }
    run_tool "nmap" nmap -O -sV --script=vulners -p 1-65535 -vv -T4 --reason -sS -sU -sC -oX '/home/treadsoftly/Desktop/leverage2.xml' -oN '/home/treadsoftly/Desktop/leverage2.txt' -oG '/home/treadsoftly/Desktop/leverage2.gnmap' --webxml --min-parallelism=14 "scanme.nmap.org"
    
    report_file="${out_folder}/report.txt"
    echo "Scan results have been compiled in $report_file"
    echo "Final report is located at ${report_file}"

    if command -v bzip2 &> /dev/null; then
        bzip2 -9 "${out_folder}/nmap/nmap_os_scan_${scan_type}.xml" "${out_folder}/nmap/nmap_os_scan_${scan_type}.txt" "${out_folder}/nmap/nmap_os_scan_${scan_type}.gnmap" &
    fi
    if command -v xz &> /dev/null; then
        xz -9 "${out_folder}/nmap/nmap_os_scan_${scan_type}.xml" "${out_folder}/nmap/nmap_os_scan_${scan_type}.txt" "${out_folder}/nmap/nmap_os_scan_${scan_type}.gnmap" &
    fi

    echo "Nmap OS scan results are located at ${out_folder}/nmap/nmap_os_scan_${scan_type}.xml.gz, ${out_folder}/nmap/nmap_os_scan_${scan_type}.xml.bz2, ${out_folder}/nmap/nmap_os_scan_${scan_type}.xml.xz"
    echo "Nmap OS scan results are located at ${out_folder}/nmap/nmap_os_scan_${scan_type}.txt.gz, ${out_folder}/nmap/nmap_os_scan_${scan_type}.txt.bz2, ${out_folder}/nmap/nmap_os_scan_${scan_type}.txt.xz"
    echo "Nmap OS scan results are located at ${out_folder}/nmap/nmap_os_scan_${scan_type}.gnmap.gz, ${out_folder}/nmap/nmap_os_scan_${scan_type}.gnmap.bz2, ${out_folder}/nmap/nmap_os_scan_${scan_type}.gnmap.xz"
}

iSpy "$@"
