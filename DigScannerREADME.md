
<p align="center">
  <img src="https://github.com/TreadSoftly/Projects/assets/121847455/dc32b4c0-b78d-4756-bfec-863283d9d641" alt="bug">
</p>

<h1 align="center">🚀 <strong>dig_iSpy</strong>: DNS Enumeration Bash Script</h1>

<p align="center">
  <em>THIS IS JUST A TEMPLATE I USE TO DROP IN AND TEST THINGS WITH dig</em>
</p>

<p align="center">
  <strong>🚨 BUGGY AS HELL AS A STANDALONE SCRIPT 🚨</strong>
</p>
<br>
<br>

## 📝 Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## 📋 Overview
`dig_iSpy` is a powerful shell script designed for DNS enumeration, leveraging `dig` and other compression tools. It provides extensive flexibility with customizable timeouts and retry attempts. Get insights into your target's DNS setup with ease and save the results in multiple compressed formats!

## 🔧 Installation
Clone the repository and ensure that you have the required tools (`dig`, `gzip`, `bzip2`, `xz`) installed on your system.

\```bash
git clone https://github.com/yourusername/dig_iSpy.git
cd dig_iSpy
chmod +x dig_iSpy.sh
\```

## 🎮 Usage
### Basic Command
\```bash
./dig_iSpy.sh [target] [timeout] [max_retries]
\```
- **target**: The target domain or IP address.
- **timeout**: The time (in seconds) to wait for a response from dig (default: 10).
- **max_retries**: The maximum number of retries for dig (default: 3).

### Options
- **-h**, **--help**, **-?**, **--?**: Show the help message and exit.

### Example
\```bash
./dig_iSpy.sh example.com 5 2
\```

## 🚀 Features
- 🎯 Targeted DNS Enumeration
- ⏰ Customizable Timeout and Retry Settings
- 📂 Output in Various Compressed Formats
- 📝 Clean and Efficient Logging

## 🤝 Contributing
If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcomed.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 📞 Contact
For any inquiries or support, please contact the maintainer at [your-email@example.com](mailto:your-email@example.com).

## 📜 SPECIFICALLY FOR THIS SCRIPT

\```bash
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

    run_tool "dig" "dig +nocmd $target +noall +answer +dnssec -t any +bufsize=4096 +time=$timeout +retry=$max_retries -4 -6 @8.8.8.8 | sed -e '/;/d' -e 's/^[ 	]*//;s/[ 	]*$//'" "${out_folder}/dns_enum.txt"
    
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
\```
</p>


Better, aesthetic, more appealing
