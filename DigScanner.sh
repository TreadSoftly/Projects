#!/bin/bash

function dig_iSpy() {
    if [ "$#" -lt 1 ]; then
        show_help
        exit 1
    fi

    target=$1
    out_folder="$HOME/Desktop/DIG_LEVERAGE_$(date +%Y-%m-%d_%H-%M-%S)"
    timeout="${2:-10}"
    max_retries="${3:-3}"
    dns_enum_json="${out_folder}/dns_enum.json"

    if ! ping -c 1 "$target" &> /dev/null; then
        echo "$target is not reachable"
        exit 1
    fi

    mkdir -p "${out_folder}/dig"

    function run_tool() {
        local tool=$1
        local command=$2
        local output_file=$3

        if command -v "$tool" &> /dev/null; then
            (eval "$command" &> "${output_file}" 2> /dev/null) &
        else
            echo "$tool is not installed. Skipping $tool."
        fi
    }

    run_tool "dig" "dig +nocmd $target +noall +answer +dnssec -t any +bufsize=4096 +time=$timeout +retry=$max_retries -4 -6 @8.8.8.8 | sed -e '/;/d' -e 's/^[ \t]*//;s/[ \t]*$//'" "${out_folder}/dns_enum.txt"
    
    echo "DNS enumeration results are located at ${dns_enum_json}.gz, ${dns_enum_json}.bz2, ${dns_enum_json}.xz"
}

show_help() {
    echo "Usage: dig_iSpy [target] [timeout] [max_retries]"
    echo ""
    echo "target       The target domain or IP address."
    echo "timeout      The time (in seconds) to wait for a response from dig (default: 10)."
    echo "max_retries  The maximum number of retries for dig (default: 3)."
}

case "$1" in
    -h|--help|-\?|--\?)
        show_help
        exit 0
        ;;
    *)
        dig_iSpy "$@"
        ;;
esac

if command -v gzip &> /dev/null; then
    gzip -9 "${dns_enum_json}" &
fi

if command -v bzip2 &> /dev/null; then
    bzip2 -9 "${dns_enum_json}" &
fi

if command -v xz &> /dev/null; then
    xz -9 "${dns_enum_json}" &
fi
