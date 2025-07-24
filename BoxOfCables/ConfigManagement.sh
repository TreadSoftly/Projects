# Configuration file
source /path/to/config.file


# SCRIPT FOR AUTO PULLING AND USING CONFIGURATION FILES (will include the logging feature)
#!/bin/bash

# If Python3 is not installed, install it
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing now..."
    apt-get -qq install -y python3
fi

# If jq is not installed, install it
if ! command -v jq &> /dev/null; then
    echo "jq is not installed. Installing now..."
    apt-get -qq install -y jq
fi

# If yaml is not installed, install it
if ! python3 -c "import yaml" &> /dev/null; then
    echo "Python3 yaml module is not installed. Installing now..."
    python3 -m pip install pyyaml
fi

# If configparser is not installed, install it
if ! python3 -c "import configparser" &> /dev/null; then
    echo "Python3 configparser module is not installed. Installing now..."
    python3 -m pip install configparser
fi

# If xmltodict is not installed, install it
if ! python3 -c "import xmltodict" &> /dev/null; then
    echo "Python3 xmltodict module is not installed. Installing now..."
    python3 -m pip install xmltodict
fi

# Default configuration file
CONFIG_FILE="/path/to/config.file"

# If a command line argument is provided, use it as the configuration file
if [ "$#" -eq 1 ]; then
    CONFIG_FILE="$1"
fi

# Extract values from configuration
LOG_LEVEL=$(python3 -c "import json, xmltodict, yaml, configparser; conf = '${CONFIG_FILE}'; result = '';\
if conf.endswith('.json'):\
    with open(conf, 'r') as f:\
        config = json.load(f);\
        result = config['log_config']['log_level'];\
elif conf.endswith('.xml'):\
    with open(conf, 'r') as f:\
        config = xmltodict.parse(f.read());\
        result = config['log_config']['log_level'];\
elif conf.endswith('.yaml') or conf.endswith('.yml'):\
    with open(conf, 'r') as f:\
        config = yaml.safe_load(f);\
        result = config['log_config']['log_level'];\
elif conf.endswith('.ini'):\
    config = configparser.ConfigParser();\
    config.read(conf);\
    result = config['log_config']['log_level'];\
result")

LOG_FILE=$(python3 -c "import json, xmltodict, yaml, configparser; conf = '${CONFIG_FILE}'; result = '';\
if conf.endswith('.json'):\
    with open(conf, 'r') as f:\
        config = json.load(f);\
        result = config['log_config']['log_file'];\
elif conf.endswith('.xml'):\
    with open(conf, 'r') as f:\
        config = xmltodict.parse(f.read());\
        result = config['log_config']['log_file'];\
elif conf.endswith('.yaml') or conf.endswith('.yml'):\
    with open(conf, 'r') as f:\
        config = yaml.safe_load(f);\
        result = config['log_config']['log_file'];\
elif conf.endswith('.ini'):\
    config = configparser.ConfigParser();\
    config.read(conf);\
    result = config['log_config']['log_file'];\
result")

REQUIRED_PACKAGES=$(python3 -c "import json, xmltodict, yaml, configparser; conf = '${CONFIG_FILE}'; result = '';\
if conf.endswith('.json'):\
    with open(conf, 'r') as f:\
        config = json.load(f);\
        result = ' '.join(config['package_config']['required_packages']);\
elif conf.endswith('.xml'):\
    with open(conf, 'r') as f:\
        config = xmltodict.parse(f.read());\
        result = ' '.join(config['package_config']['required_packages']);\
elif conf.endswith('.yaml') or conf.endswith('.yml'):\
    with open(conf, 'r') as f:\
        config = yaml.safe_load(f);\
        result = ' '.join(config['package_config']['required_packages']);\
elif conf.endswith('.ini'):\
    config = configparser.ConfigParser();\
    config.read(conf);\
    result = ' '.join([x.strip() for x in config['package_config']['required_packages'].split(',')]);\
result")

# Define color variables for formatting output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define logging function
log() {
    local log_priority=$1
    local log_message=$2
    local date_time=$(date "+%Y-%m-%d %H:%M:%S")
    
    case ${LOG_LEVEL} in
        "DEBUG")
            echo -e "${date_time} [${log_priority}] ${log_message}"
            ;;
        "INFO")
            if [[ "${log_priority}" == "INFO" || "${log_priority}" == "WARN" || "${log_priority}" == "ERROR" || "${log_priority}" == "FATAL" ]]; then
                echo -e "${date_time} [${log_priority}] ${log_message}"
            fi
            ;;
        "WARN")
            if [[ "${log_priority}" == "WARN" || "${log_priority}" == "ERROR" || "${log_priority}" == "FATAL" ]]; then
                echo -e "${YELLOW}${date_time} [${log_priority}] ${log_message}${NC}"
            fi
            ;;
        "ERROR")
            if [[ "${log_priority}" == "ERROR" || "${log_priority}" == "FATAL" ]]; then
                echo -e "${RED}${date_time} [${log_priority}] ${log_message}${NC}"
            fi
            ;;
        "FATAL")
            if [[ "${log_priority}" == "FATAL" ]]; then
                echo -e "${RED}${date_time} [${log_priority}] ${log_message}${NC}"
                exit 1
            fi
            ;;
    esac
## NEED TO ORGANIZE AND CREATE THE WORKING DYNAMIC CONFIG MANAGEMENT TOOL FROM THESE
## PREVIOUS WORKS I HAVE FRANKENSTIEND


}
# Define an error handling function
handle_error() {
    local message=$1
    local exit_code=${2:-1}
    log "FATAL" "${message}"
    exit ${exit_code}
}




# Function to generate configuration
function func_generate_config {
    echo "Generating configuration..."
    # Ask for user's preferences and create a JSON configuration file
    # This is just an example, modify it according to your needs
    echo "Enter log level:"
    read log_level
    echo "Enter log file path:"
    read log_file
    config="{\"log_level\":\"$log_level\", \"log_file\":\"$log_file\", \"required_packages\":[\"package1\", \"package2\"]}"
    echo "$config" > $CONFIG_FILE
}

# FROM THIS SCRIPT THE NETWORK CONFIG IS PULLED
# System Profiling
function func_system_profiling {
    func_log "Starting system profiling..." "INFO"
    # Collect hardware information
    lshw -json > hardware_profile.json
    # Collect software information
    dpkg -l > software_profile.txt
    # Collect network configuration
    ifconfig > network_profile.txt
    func_log "System profiling completed." "INFO"
}

# TOR READS AND USES THE CONFIGURATION INORDER TO BE UTILIZED
    # Start Tor and verify fingerprint
    func_log "===[ Starting Tor and Verifying Fingerprint ]===" "INFO"
    systemctl start tor
    sudo -u debian-tor tor --list-fingerprint --orport 1 --datadir /var/lib/tor/ | grep -v "Tor can't help you if you use it wrong" | grep -v "Read configuration file" | grep -v "By default, Tor does not run as an exit relay." | grep notice
    func_log "Tor started and fingerprint verified." "INFO"

# LOADING THE JSON CONFIG FILE
    # Load configuration from JSON file
    CONFIG=$(jq -c '.' "$CONFIG_FILE")
    # Extract values from configuration
    LOG_LEVEL=$(echo "$CONFIG" | jq -r '.log_level')
    LOG_FILE=$(echo "$CONFIG" | jq -r '.log_file')
    REQUIRED_PACKAGES=$(echo "$CONFIG" | jq -r '.required_packages[]')
    # Add more configurations as needed...
    echo "Configuration loaded from: $CONFIG_FILE"
