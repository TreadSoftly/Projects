#!/bin/bash

# Constants
OUT_FOLDER="output_folder"
TIMEOUT_DEFAULT=10
MAX_RETRIES_DEFAULT=3

# Function to show help
show_help() {
    echo "Usage: dig_iSpy [target] [timeout] [max_retries]"
    echo ""
    echo "target       The target domain or IP address."
    echo "timeout      The time (in seconds) to wait for a response from dig (default: ${TIMEOUT_DEFAULT})."
    echo "max_retries  The maximum number of retries for dig (default: ${MAX_RETRIES_DEFAULT})."
}

# Function to identify target type
target_input_type() {
  local input_str="$1"
  # Patterns to identify the target type
  local patterns=(
    "ip|^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    "domain|^(?:[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$"
    "port|^\d{1,5}$"
    "mac|^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    "url|^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w._~:/?#[\]@!$&()*+,;=]*)?$"
    "asn|^AS\d+$"
  )

  for pattern in "${patterns[@]}"; do
    IFS="|" read -r type regex <<< "$pattern"
    if [[ $input_str =~ $regex ]]; then
      echo "$type"
      return
    fi
  done

  echo "unknown"
}

# Function to run a tool
run_tool() {
    local tool="$1"
    local command="$2"
    local output_file="$3"

    if command -v "$tool" &> /dev/null; then
        (eval "$command" &> "${output_file}" 2> /dev/null) &
    else
        echo "$tool is not installed. Skipping $tool."
    fi
}

# Main function
dig_iSpy() {
    if [ "$#" -lt 1 ]; then
        show_help
        exit 1
    fi

    local target="$1"
    local timeout="${2:-${TIMEOUT_DEFAULT}}"
    local max_retries="${3:-${MAX_RETRIES_DEFAULT}}"
    local target_type
    target_type=$(target_input_type "$target")

    if [[ $target_type == "unknown" || -z "$target" ]]; then
      echo "Invalid or empty target: $target"
      exit 1
    fi

    if ! ping -c 1 "$target" &> /dev/null; then
        echo "$target is not reachable"
        exit 1
    fi

    mkdir -p "${OUT_FOLDER}/dig"
    local command="dig +nocmd $target +noall +answer +dnssec -t any +bufsize=4096 +time=$timeout +retry=$max_retries -4 -6 @8.8.8.8 | sed -e '/;/d' -e 's/^[ \t]*//;s/[ \t]*$//'"
    run_tool "dig" "$command" "${OUT_FOLDER}/dns_enum.txt"
    
    echo "DNS enumeration results are located at ${dns_enum_json}.gz, ${dns_enum_json}.bz2, ${dns_enum_json}.xz"
}

# Main execution flow
case "$1" in
    -h|--help|-\?|--\?)
        show_help
        exit 0
        ;;
    *)
        dig_iSpy "$@"
        ;;
esac

# Compression of results
gzip -9 "${dns_enum_json}" &> /dev/null &
bzip2 -9 "${dns_enum_json}" &> /dev/null &
xz -9 "${dns_enum_json}" &> /dev/null &
