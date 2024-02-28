# Recently updated, still trying to make the version 1 open source code better as it will be the core code for setting up and running Kali Boxes for in field use

function asdf() {
    # Set colors for formatting output
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color

    # Activate virtual environment
    printf "${YELLOW}===[ Activating Virtual Environment ]===${NC}\n"
    apt install python3-venv -y >/dev/null 2>&1 
    python3 -m venv myvenv
    source myvenv/bin/activate

    # Check and install required packages
    printf "${YELLOW}===[ Checking and Installing Required Packages ]===${NC}\n"
    declare -a packages=("python3-venv" "tor" "proxychains4" "macchanger" "torsocks" "grc")
    for package in "${packages[@]}"; do
        if ! dpkg-query -W -f='${Status}' "$package" >/dev/null 2>&1 | grep -q "install ok installed"; then
            sudo apt-get -qq install -y "$package" >/dev/null 2>&1
            printf "${GREEN}Installed: ${package}${NC}\n"
        else
            printf "${BLUE}Already installed: ${package}${NC}\n"
        fi
    done

    # Install Anonsurf if it's not installed
    if ! command -v anonsurf &> /dev/null; then
        printf "${YELLOW}===[ Installing Anonsurf ]===${NC}\n"
        git clone -qq https://github.com/Und3rf10w/kali-anonsurf.git
        cd kali-anonsurf
        ./installer.sh >/dev/null 2>&1
        cd ..
        printf "${GREEN}Anonsurf installed.${NC}\n"
    else
        printf "${BLUE}Anonsurf already installed.${NC}\n"
    fi

    # Update and upgrade Kali Linux
    printf "${YELLOW}===[ Updating and Upgrading Kali Linux ]===${NC}\n"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y && apt-get upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" && apt-get dist-upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" && apt-get autoremove -y && apt-get autoclean -y
    unset DEBIAN_FRONTEND
    printf "${GREEN}Kali Linux updated and upgraded.${NC}\n"

    # Uncomment dynamic_chain option in proxychains4.conf
    if ! grep -q "^dynamic_chain" /etc/proxychains4.conf; then
        sed -i 's/^#dynamic_chain$/dynamic_chain/' /etc/proxychains4.conf
    fi

    # Check and install systemd-resolved
    if ! dpkg-query -W -f='${Status}' systemd-resolved >/dev/null 2>&1 | grep -q "install ok installed"; then
        apt-get -qq install systemd-resolved -y >/dev/null 2>&1
    fi

    # Configure DNS settings
    printf "${YELLOW}===[ Configuring DNS Settings ]===${NC}\n"
    if [ ! -f "/etc/systemd/resolved.conf.backup" ]; then
        cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.backup
    fi
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
    printf "${GREEN}DNS settings configured.${NC}\n"

    # System Information
    printf "${YELLOW}===[ System Information ]===${NC}\n"
    
    printf "\n${GREEN}Filesystem Information:${NC}\n"
    df -h --output=source,fstype,size,used,avail,pcent,target \
        | awk 'NR==1{print; next} {print $0 | "grep --color=always /"}' \
        | column -t

    printf "\n${YELLOW}Memory Information:${NC}\n"
    free -h | grep --color=always -E "^Mem|^Swap"

    printf "\n${BLUE}Network Interface Information:${NC}\n"
    ip -c -br addr

    printf "\n${RED}PCI Devices Information:${NC}\n"
    lspci -mm

    printf "\n${GREEN}USB Devices Information:${NC}\n"
    lsusb

    printf "\n${YELLOW}Block Devices Information:${NC}\n"
    lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT

    # Add a route to bypass Anonsurf for local network traffic
    if ! ip route show | grep -q "192.168.0.0/24 dev eth0"; then
        ip route add 192.168.0.0/24 dev eth0
    fi

    # Start Tor and verify fingerprint
    printf "${YELLOW}===[ Starting Tor and Verifying Fingerprint ]===${NC}\n"
    systemctl start tor
    sudo -u debian-tor tor --list-fingerprint --orport 1 --datadir /var/lib/tor/ \
        | grep -v "Tor can't help you if you use it wrong" \
        | grep -v "Read configuration file" \
        | grep -v "By default, Tor does not run as an exit relay." \
        | grep notice
    printf "${GREEN}Tor started and fingerprint verified.${NC}\n"

    # Restart anonsurf and get status and IP
    printf "${YELLOW}===[ Restarting Anonsurf and Getting Status and IP ]===${NC}\n"
    anonsurf start

    # Change MAC address of eth0 interface
    printf "${YELLOW}===[ Changing MAC address of eth0 ]===${NC}\n"
    interface=eth0
    old_mac=$(ip link show $interface | awk '/ether/ {print $2}')

    # Generate a random MAC address
    new_mac=$(printf '02:%02x:%02x:%02x:%02x:%02x' $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)))
    ip link set dev $interface down
    ip link set dev $interface address $new_mac
    ip link set dev $interface up
    printf "Changed MAC address of ${BLUE}${interface}${NC} from ${GREEN}${old_mac}${NC} to ${BLUE}${new_mac}${NC}\n"

    # Get and print permanent and current MAC Addresses for eth0
    printf "\n${YELLOW}Current and Permanent MAC Addresses:${NC}\n"
    mac_output=$(macchanger -s eth0)
    current_mac=$(echo "$mac_output" | grep "Current MAC" | awk '{print $3}')
    permanent_mac=$(echo "$mac_output" | grep "Permanent MAC" | awk '{print $3}')
    printf "${BLUE}Permanent MAC:${NC} ${permanent_mac}\n"
    printf "${GREEN}Current MAC:${NC}   ${current_mac}\n"

    # Check if mtr-tiny or mtr is installed, and install if not
    if ! command -v mtr-tiny &> /dev/null; then
        apt-get -qq install mtr-tiny >/dev/null 2>&1
        printf "${GREEN}mtr-tiny installed.${NC}\n"
    fi
    if ! command -v mtr &> /dev/null; then
        apt-get -qq install mtr >/dev/null 2>&1
        printf "${GREEN}mtr installed.${NC}\n"
    fi

    # Run mtr command against Google with advanced options and colored output
    printf "${YELLOW}===[ Running mtr against Google ]===${NC}\n"
    grc mtr -T -r -c 1 -i 0.1 -I eth0 -n --displaymode 2 8.8.8.8

}
