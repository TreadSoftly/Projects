 target_input_type() {
  local input_str=$1
  local ip_pattern='^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
  local domain_pattern='^(?:[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$'
  local port_pattern='^\d{1,5}$'
  local mac_pattern='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
  local url_pattern='^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w._~:/?#[\]@!$&()*+,;=]*)?$'
  local asn_pattern='^AS\d+$'

  if [[ $input_str =~ $ip_pattern ]]; then
    echo "ip"
  elif [[ $input_str =~ $domain_pattern ]]; then
    echo "domain"
  elif [[ $input_str =~ $port_pattern ]]; then
    echo "port"
  elif [[ $input_str =~ $mac_pattern ]]; then
    echo "mac"
  elif [[ $input_str =~ $url_pattern ]]; then
    echo "url"
  elif [[ $input_str =~ $asn_pattern ]]; then
    echo "asn"
  else
    echo "unknown"
  fi
 }
 
 read -p "Enter IP, domain, port, MAC address, URL, or ASN: " target
 
 target_type=$(target_input_type "$target")
 if [[ $target_type == "unknown" ]]; then
  echo "Invalid input: $target"
  exit 1
 fi
 
 if [ -z "$target" ]; then
  echo "No target specified."
  exit 1
 fi
