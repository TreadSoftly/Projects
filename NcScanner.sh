#!/bin/bash

function print_help() {
    echo "Usage: $(basename "$0") [options] TARGET"
    echo
    echo "Options:"
    echo "  -h, --help       Display this help message"
    echo "  -p, --port       Specify the port range for the scan (default: 0-65535)"
    echo "  -o, --output     Specify the output directory"
}

function nc_iSpy() {
    if [ "$#" -lt 1 ]; then
        print_help
        exit 1
    fi

    target=$1
    port="${2:-"0-65535"}"
    out_folder="${3:-"${HOME}/Desktop/NC_SCAN_$(date +%Y-%m-%d_%H-%M-%S)"}"

    if ! ping -c 1 "$target" &> /dev/null; then
        echo "$target is not reachable"
        exit 1
    fi

    mkdir -p "${out_folder}/nc"

    function run_tool() {
        local tool=$1
        local command=$2
        local output_file=$3
        
        if command -v "$tool" &> /dev/null; then
            eval "$command" &> "${output_file}" 2> /dev/null
        else
            echo "$tool is not installed. Skipping $tool."
        fi
    }

    run_tool "nc" 'nc -v -z "$target" "$port" | grep -v "Connection to" | sed '\''s/^[ \t]*//;s/[ \t]*$//'\''' "${out_folder}/nc/nc_scan.txt"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help)
            print_help
            exit 0
            ;;
        -p|--port)
            port_arg="$2"
            shift 2
            ;;
        -o|--output)
            output_arg="$2"
            shift 2
            ;;
        *)
            if [ -z "${target_arg}" ]; then
                target_arg="$1"
            else
                echo "Error: Invalid argument or too many arguments"
                exit 1
            fi
            shift
            ;;
    esac
done

nc_iSpy "${target_arg}" "${port_arg}" "${output_arg}"
