# THIS NEEDS TO BE BROKEN OUT FROM MONOLITHIC asdf FUNCTION (I goofed arouned with an alias command 'asdf' so much I now need to turn it inot a tool)
# There are current impacting bugs to pick through. Planned on testing it out when I break it apart from its monolithic form and pure bash buildout


function asdf() {
    # Set colors for formatting output
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color

    # Create the directory if it does not exist
    create_log_directory() {
    local log_directory=$(dirname "${LOG_FILE}")
    [ ! -d "${log_directory}" ] && mkdir -p "${log_directory}"

    # Log file path (change to your desired log file path)
    LOG_FILE="/path/to/your/logfile.log"

    # Network interface name (replace with your desired interface name)
    INTERFACE_NAME="eth0"

    # Define progress bar function
    progress_bar() {
    local label=$1
    local percent=$2
    if [ "$percent" -lt 0 ] || [ "$percent" -gt 100 ]; then
        printf "Error: percentage value must be between 0 and 100.\n"
        return 1
    fi
    printf "$label: \e[32m[\e[0m"
    for i in $(seq 1 "$percent"); do printf "\e[32m=\e[0m"; done
    for i in $(seq 1 $(($percent+1)) 100); do printf " "; done
    printf "\e[32m] $percent%% completed\e[0m\n"
    # Print additional progress information
    if [ "$percent" -eq 0 ]; then
        printf "$label: No progress has been made.\n"
    elif [ "$percent" -lt 50 ]; then
        printf "$label: Progress is slow.\n"
    elif [ "$percent" -ge 50 ] && [ "$percent" -lt 75 ]; then
        printf "$label: Progress is moderate.\n"
    elif [ "$percent" -ge 75 ] && [ "$percent" -lt 90 ]; then
        printf "$label: Progress is good.\n"
    elif [ "$percent" -ge 90 ] && [ "$percent" -lt 100 ]; then
        printf "$label: Progress is almost complete.\n"
    elif [ "$percent" -eq 100 ]; then
        printf "$label: Progress is complete.\n"
    fi
}

function spin() {
    local message="$1"
    local pid=$2
    local delay=0.1
    local spinstr='|/-\'
    local i=0
    tput civis # Hide cursor
    while kill -0 $pid 2>/dev/null; do
        local temp=${spinstr#?}
        printf " \r${!color}${spinstr:0:1} ${message}${NC}"
        local spinstr=${temp}${spinstr%"$temp"}
        sleep $delay
        i=$(( (i+1) % 4 ))
        case $i in
            0) local color_var_name="YELLOW";;
            1) local color_var_name="BLUE";;
            2) local color_var_name="GREEN";;
            3) local color_var_name="RED";;
        esac
        local color
        eval "color=\$$color_var_name" # Get the value of the variable by its name
    done
    printf " \r"
    tput cnorm # Show cursor
}

    # Logging function
    log() {
        # Create the directory if it does not exist
        local log_directory=$(dirname "${LOG_FILE}")
        [ ! -d "${log_directory}" ] && mkdir -p "${log_directory}"
        local log_priority="$1"
        local log_message="$2"
        local date_time
        date_time=$(date "+%Y-%m-%d %H:%M:%S")
        local log_color
        echo -e "${date_time} [${log_priority}] ${log_message}" >> "${LOG_FILE}"
	
    }

        # Define log colors based on priority
        case ${log_priority} in
            "INFO")  log_color="${BLUE}" ;;
            "WARN")  log_color="${YELLOW}" ;;
            "ERROR") log_color="${RED}" ;;
            "FATAL") log_color="${RED}" ;;
            *)       log_color="${NC}" ;;
        esac

        # Log to console
        echo -e "${log_color}${date_time} [${log_priority}] ${log_message}${NC}"

        # Log to file
        echo -e "${date_time} [${log_priority}] ${log_message}" >> ${LOG_FILE}

        # Exit if fatal error
        [[ "${log_priority}" == "FATAL" ]] && exit 1
    }

    create_directory_and_files() {
        local dir_name="$1"
        local file_name="$2"
        local user_id="$3"
        local timestamp=$(date "+%Y-%m-%d %H:%M:%S")

        mkdir -p "${dir_name}/${user_id}/${timestamp}" || { log "ERROR" "Failed to create directory"; return 1; }
        touch "${dir_name}/${user_id}/${timestamp}/${file_name}.txt" || log "WARN" "Failed to create txt file"
        touch "${dir_name}/${user_id}/${timestamp}/${file_name}.csv" || log "WARN" "Failed to create csv file"
        touch "${dir_name}/${user_id}/${timestamp}/${file_name}.json" || log "WARN" "Failed to create json file"
        touch "${dir_name}/${user_id}/${timestamp}/${file_name}.xml" || log "WARN" "Failed to create xml file"
        touch "${dir_name}/${user_id}/${timestamp}/${file_name}.ini" || log "WARN" "Failed to create ini file"
    }

    # Function to convert JSON to CSV (requires jq)
    convert_json_to_csv() {
        local json_file="$1"
        local csv_file="$2"
        jq -r '(.[0] | keys_unsorted) as $keys | $keys, map([.[ $keys[] ]])[] | @csv' "$json_file" > "$csv_file"
    }

    # ASCII progress bar function
    progress_bar() {
        local task="$1"
        local percent="$2"
        local width=50
        local filled=$(printf "%.0f" $(echo "$width * $percent / 100" | bc -l))
        local empty=$((width - filled))
        printf "\r${task}: [${GREEN}%-*s${NC}${BLUE}%-*s${NC}] ${percent}%%" "${filled}" "$(printf '%0.s=' {1..${filled}})" "${empty}" "$(printf '%0.s ' {1..${empty}})"
    }

    # Timer countdown function
    timer_countdown() {
        local time="$1"
        local task="$2"
        while [ ${time} -gt 0 ]; do
            printf "\r${task} will be completed in ${time}s..."
            sleep 1
            ((time--))
        done
        printf "\n"
    }

# Memory Analysis Prevention
func_memory_analysis_prevention() {
    printf "${BLUE}===[ Starting Memory Analysis Prevention Techniques... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Starting memory analysis prevention techniques..."
    echo "0" | tee /proc/sys/kernel/core_pattern >/dev/null
    secure_memory_allocation
    printf "${GREEN}===[ Memory Analysis Prevention Techniques Completed. ]===${NC}\n"
    log "${GREEN}INFO${NC}" "Memory analysis prevention techniques completed."
}

# Anti-Forensics Techniques with user input validation and selection choices
func_anti_forensics() {
    printf "${GREEN}===[ Starting Anti-Forensics Techniques... ]===${NC}\n"
    log "${GREEN}INFO${NC}" "Starting anti-forensics techniques..."
    srm -vz /tmp/zerofile
    printf "${BLUE}===[ Zeroing Bash History... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Zeroing bash history..."
    cat /dev/null > ~/.bash_history && history -c && history -w
    read -p "${YELLOW}Delete all temporary files? (y/n): ${NC}" choice
    if [ "$choice" == "y" ]; then
        printf "${RED}===[ Deleting Temporary Files... ]===${NC}\n"
        log "${RED}INFO${NC}" "Deleting temporary files..."
        rm -rf /tmp/* /var/tmp/*
    fi
    printf "${BLUE}===[ Wiping Cache Files... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Wiping cache files..."
    find /var/cache -type f -exec srm -v {} \;
    printf "${BLUE}===[ Updating File Modification Times... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Updating file modification times..."
    find / -type f -mtime +30 -exec touch -t 202301010000.00 {} \;
    printf "${BLUE}===[ Wiping Swapfile... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Wiping swapfile..."
    swapoff -a && srm -v /swapfile && swapon -a
    printf "${BLUE}===[ Wiping Log Files... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Wiping log files..."
    find /var/log -type f -exec srm -v {} \;
    printf "${BLUE}===[ Clearing User Bash History... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Clearing user bash history..."
    for user in /home/*; do
        cat /dev/null > "$user/.bash_history"
    done
    printf "${BLUE}===[ Updating File Modification Times... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Clearing thumbnails cache..."
    rm -rf ~/.cache/thumbnails/*
    printf "${BLUE}===[ Changing MAC Address... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Changing MAC address..."
    interface=$(ip link show | grep -E '^[0-9]+:' | grep -v 'lo:' | cut -d ':' -f 2 | tr -d ' ')
    ifconfig $interface down
    macchanger -r $interface
    ifconfig $interface up
    printf "${BLUE}===[ Randomizing Hostname... ]===${NC}\n"
    log "${BLUE}INFO${NC}" "Randomizing hostname..."
    hostname $(head /dev/urandom | tr -dc a-z | head -c 8)
    echo "0" | tee /proc/sys/kernel/core_pattern >/dev/null
    printf "${GREEN}===[ Anti-Forensics Techniques Completed... ]===${NC}\n"
    log "${GREEN}INFO${NC}" "Anti-forensics techniques completed."
}

    # Secure Memory Allocation (added -o option)
    secure_memory_allocation() {
        printf "${BLUE}===[ Allocating Secure Memory... ]===${NC}\n"
        log "${BLUE}INFO${NC}" "Allocating secure memory..."
        mkdir -p /secure_memory
        mount -t tmpfs -o size=512M,mode=1777 -o tmpfs /secure_memory
    }

# Memory Zeroization Functionality
    memory_zeroization() {
    local target_file="$1"
    if [ -f "$target_file" ]; then
        printf "${BLUE}===[ Zeroizing Memory For File: ${target_file}... ]===${NC}\n"
        log "${BLUE}INFO${NC}" "Zeroizing memory for file: ${target_file}..."
        dd if=/dev/zero of="$target_file" bs=1M count=$(($(stat -c %s "$target_file") / (1024 * 1024)))
        rm -f "$target_file"
    else
        printf "${RED}===[ File Not Found: ${target_file} ]===${NC}\n"
        log "${RED}ERROR${NC}" "File not found: ${target_file}"
    fi
}

    # Parse command-line arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --zeroize)
                if [ -n "$2" ]; then
                    memory_zeroization "$2"
                    shift
                else
                    printf "${RED}Error: --zeroize requires a file path argument${NC}\n"
                    exit 1
                fi
                ;;
            *)
                printf "Usage: $0 [--zeroize FILE]\n"
                exit 1
                ;;
        esac
        shift
    done

    # Check and install required packages dynamically
    check_and_install_packages() {
        printf "${BLUE}===[ Checking & Installing Required Packages... ]===${NC}\n"
        log "INFO" "===[ Checking and Installing Required Packages ]==="
        declare -a packages=("python3-venv" "tor" "proxychains4" "macchanger" "torsocks" "grc" "srm" "arp-scan" "mtr-tiny" "mtr")
        for package in "${packages[@]}"; do
            if ! dpkg-query -W -f='${Status}' "$package" >/dev/null 2>&1 | grep -q "install ok installed"; then
                apt -qq install -y "$package" >/dev/null 2>&1 &
                local pid=$!
                spin "Downloading ${package}..." $pid
                wait $pid
                printf "${GREEN}INFO${NC} ${GREEN}===[ Installed: ${package} ]===${NC}\n"
		local pid=$!
                spin "Downloading ${package}..." $pid
                wait $pid
                log "INFO" "Installed: ${package}"
            else
                printf "${BLUE}INFO${NC} ${BLUE}===[ Already Installed: ${package} ]===${NC}\n"
                log "INFO" "Already installed: ${package}"
            fi
        done
    }

    # Activate virtual environment
    printf "${GREEN}===[ Activating Python3-myvnv ]===${NC}\n"    
    log "INFO" "===[ Activating Virtual Environment ]==="
    apt install python3-venv -y >/dev/null 2>&1
    python3 -m venv myvenv
    source myvenv/bin/activate

    # Print Header for System Information
    print_header() {
        local header="$1"
        local color="$2"
        printf "\n${color}${header}${NC}\n"
        log "INFO" "$header"
    }

    # Install Anonsurf if its not installed
    if ! command -v anonsurf &> /dev/null; then
        printf "${BLUE}===[ Installing Anonsurf ]===${NC}\n"    
        log "INFO" "===[ Installing Anonsurf ]==="
        git clone -qq https://github.com/Und3rf10w/kali-anonsurf.git
        cd kali-anonsurf
        ./installer.sh >/dev/null 2>&1
        cd ..
        printf "${GREEN}===[ Anonsurf Installed ]===${NC}\n"  
        log "INFO" "Anonsurf installed."
    else
        printf "${YELLOW}===[ Anonsurf Already Installed ]===${NC}\n"  
        log "INFO" "Anonsurf already installed."
    fi
    
    # Update and upgrade Kali Linux
    printf "${GREEN}===[ Updating and Upgrading Kali Linux ]===${NC}\n"
    printf "${YELLOW}===[ THIS WILL TAKE SOME TIME ON FIRST INSTALL... ]===${NC}\n"
    log "INFO" "===[ Updating and Upgrading Kali Linux ]==="
    export DEBIAN_FRONTEND=noninteractive
    apt update --quiet=2 -y >/dev/null 2>&1 && apt full-upgrade --quiet=2 -y -o >/dev/null 2>&1 Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" && apt dist-upgrade --quiet=2 -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" >/dev/null 2>&1 && apt autoremove --quiet=2 -y >/dev/null 2>&1 && apt autoclean --quiet=2 -y >/dev/null 2>&1
    unset DEBIAN_FRONTEND
    log "INFO" "Kali Linux updated and upgraded."

    # Uncomment dynamic_chain option in proxychains4.conf
    printf "${YELLOW}===[ Upgrading Proxychains from ProxyChains3 Static to ProxyChains4 Dynamic ]===${NC}\n"
    if ! grep -q "^dynamic_chain" /etc/proxychains4.conf; then
        sed -i 's/^#dynamic_chain$/dynamic_chain/' /etc/proxychains4.conf
    fi

    # Check and install systemd-resolved
    if ! dpkg-query -W -f='${Status}' systemd-resolved >/dev/null 2>&1 | grep -q "install ok installed"; then
        apt -qq install systemd-resolved -y >/dev/null 2>&1
    fi

printf "${YELLOW}===[ Configuring DNS Settings With Google & CloudFlare DNS then Local and Failover DNS backups ]===${NC}\n"
log "INFO" "===[ Configuring DNS Settings ]==="

if [ ! -f "/etc/systemd/resolved.conf.backup" ]; then
    cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.backup
    log "INFO" "Backup created for original DNS settings."
fi

# Apply new DNS settings
tee /etc/systemd/resolved.conf >/dev/null <<EOF
[Resolve]
DNS=8.8.8.8 8.8.4.4 1.1.1.1 1.0.0.1 
FallbackDNS=9.9.9.9 149.112.112.112
Cache=yes
CacheSize=100M
CacheTimeSec=300
DNSOverTLS=yes
DNSOverTLSPort=853
DNSOverTLSCertificateDepth=2
DNSOverTLSServerName=cloudflare-dns.com
MulticastDNS=yes
LLMNR=yes
EOF

systemctl restart systemd-resolved

# Simulate checking connectivity
printf "${BLUE}===[ Checking Connectivity to Google & CloudFlare DNS... ]===${NC}\n"
for i in $(seq 0 5 100); do
    progress_bar $i
    sleep 0.1
done
printf "\n"

# Check connectivity to Google's DNS
if ! ping -c 1 8.8.8.8 &>/dev/null; then
    log "WARN" "Failed to connect to Google & CloudFlare DNS. Reverting to local system DNS."

    # Revert to original configuration from backup
    cp /etc/systemd/resolved.conf.backup /etc/systemd/resolved.conf
    systemctl restart systemd-resolved
    log "INFO" "Restored original DNS settings."
    printf "${GREEN}DNS settings restored to original configuration.${NC}\n"
else
    log "INFO" "DNS settings configured successfully with Google & CloudFlare DNS."
    printf "${GREEN}DNS settings configured.${NC}\n"
fi

    systemctl restart systemd-resolved
    printf "${GREEN}DNS settings configured.${NC}\n"
    log "INFO" "DNS settings configured."

    # Print a row with two columns
    print_row() {
        local col1="$1"
        local col2="$2"
        local color="$3"
        printf "${color}%-30s %-50s${NC}\n" "$col1" "$col2"
    }

    # System Information
    printf "${YELLOW}===[ System Information ]===${NC}\n"
    log "INFO" "===[ System Information ]==="
    
    printf "\n${GREEN}Filesystem Information:${NC}\n"
    log "INFO" "\nFilesystem Information:"
    df -h --output=source,fstype,size,used,avail,pcent,target \
        | awk 'NR==1{print; next} {print $0 | "grep --color=always /"}' \
        | column -t

    printf "\n${YELLOW}Memory Information:${NC}\n"
    log "INFO" "\nMemory Information:"
    free -h | grep --color=always -E "^Mem|^Swap"

    printf "\n${BLUE}Network Interface Information:${NC}\n"
    log "INFO" "\nNetwork Interface Information:"
    ip -c -br addr

    print_header "PCI Devices Information:" "${BLUE}"
    lspci -mm | while read -r line; do
        IFS='" "' read -r slot class vendor device rev prog interface <<<"$line"
        log "INFO" "\nUSB $class $vendor $device:"
        print_row "$slot" "$class $vendor $device" "${BLUE}"
    done

    printf "\n${GREEN}USB Devices Information:${NC}\n"
    log "INFO" "\nUSB Devices Information:"
    lsusb

    printf "\n${YELLOW}Block Devices Information:${NC}\n"
    log "INFO" "\nBlock Devices Information:"
    lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT | while read -r line; do
    IFS=' ' read -r name size fstype mountpoint <<<"$line"
    print_row "$name" "$size $fstype $mountpoint" "${YELLOW}"
    done

    # Add a route to bypass Anonsurf for local network traffic
    printf "\n${BLUE}Add a route to bypass Anonsurf for local network traffic${NC}\n"
    if ! ip route show | grep -q "192.168.0.0/24 dev eth0"; then
        ip route add 192.168.0.0/24 dev eth0
    fi

    # Start Tor and verify fingerprint (fixed syntax)
    printf "${YELLOW}===[ Starting Tor and Verifying Fingerprint ]===${NC}\n"
    log "INFO" "===[ Starting Tor and Verifying Fingerprint ]==="
    systemctl start tor
    sudo -u debian-tor tor --list-fingerprint --orport 1 --datadir /var/lib/tor/ \
        | grep -v "Tor can't help you if you use it wrong" \
        | grep -v "Read configuration file" \
        | grep -v "By default, Tor does not run as an exit relay." \
        | grep "notice"
    printf "${GREEN}Tor started and fingerprint verified.${NC}\n"
    log "INFO" "Tor started and fingerprint verified."

    # Restart anonsurf and get status and IP
    printf "${YELLOW}===[ Restarting Anonsurf and Getting Status and IP ]===${NC}\n"
    log "INFO" "===[ Restarting Anonsurf and Getting Status and IP ]==="
    anonsurf start
    anonsurf status
    anonsurf myip

    # ARP scan download check
    if ! command -v arp-scan &> /dev/null; then
        printf "${YELLOW}===[ Downloading arp-scan ]===${NC}\n"
        log "INFO" "===[ Downloading arp-scan ]==="
        apt -qq install arp-scan >/dev/null 2>&1 &
        pid=$!
        spin='-\|/'
        i=0
        while kill -0 $pid 2>/dev/null; do
            i=$(( (i+1) %4 ))
            printf "\r${spin:$i:1} Downloading..."
            sleep .1
        done
        printf "${GREEN}===[ arp-scan installed ]===${NC}\n"
        log "INFO" "arp-scan installed."
    fi

    # Change MAC Address Using ARP Scanner
    change_mac_address() {
        log "INFO" "===[ Changing MAC address using ARP scanner ]==="
        local interface=eth0
        local arp_output=$(sudo arp-scan -l)
        local similar_mac=$(echo "$arp_output" | grep -E -o '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | shuf -n 1)
        if [ -z "$similar_mac" ]; then
            # Fallback to Random MAC if Similar MAC Not Found
            local old_mac=$(ip link show $interface | awk '/ether/ {print $2}')
            ip link set dev $interface down
            macchanger -r $interface
            ip link set dev $interface up
            local new_mac=$(ip link show $interface | awk '/ether/ {print $2}')
            printf "Changed MAC address of ${BLUE}${interface}${NC} from ${GREEN}${old_mac}${NC} to ${BLUE}${new_mac}${NC}\n"
            log "INFO" "Changed MAC address of ${interface} from ${old_mac} to ${new_mac}."
        else
            local old_mac=$(ip link show $interface | awk '/ether/ {print $2}')
            ip link set dev $interface down
            ip link set dev $interface address $similar_mac
            ip link set dev $interface up
            printf "Changed MAC address of ${BLUE}${interface}${NC} from ${GREEN}${old_mac}${NC} to ${BLUE}${similar_mac}${NC}\n"
            log "INFO" "Changed MAC address of ${interface} from ${old_mac} to ${similar_mac}."
        fi
    }

    # Check if mtr-tiny or mtr is installed, and install if not
    if ! command -v mtr-tiny &> /dev/null; then
        apt -qq install mtr-tiny >/dev/null 2>&1
        printf "${GREEN}mtr-tiny installed.${NC}\n"
        log "INFO" "mtr-tiny installed."
    fi
    if ! command -v mtr &> /dev/null; then
        apt -qq install mtr >/dev/null 2>&1
        printf "${GREEN}mtr installed.${NC}\n"
        log "INFO" "mtr installed."
    fi
    # Check and install grc
    if ! dpkg-query -W -f='${Status}' grc >/dev/null 2>&1 | grep -q "install ok installed"; then
        apt -qq install grc -y >/dev/null 2>&1
        printf "${GREEN}grc installed.${NC}\n"
        log "INFO" "grc installed."
    fi
    # Run mtr command against Google for a network check with advanced options and colored output
    printf "${YELLOW}===[ Running mtr against Google ]===${NC}\n"
    log "INFO" "===[ Running mtr against Google ]==="
    grc mtr -T -r -c 1 -i 0.1 -I eth0 -n --displaymode 2 8.8.8.8
    
    log "INFO" "Script execution completed."
    
    bash
}

alias asdf='asdf'
