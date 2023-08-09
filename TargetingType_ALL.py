import re

def target_input_type(input_str):
    # Define regular expression patterns for different target types
    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    domain_pattern = r'^(?:[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$'
    port_pattern = r'^\d{1,5}$'
    mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    url_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w._~:/?#[\]@!$&()*+,;=]*)?$'
    asn_pattern = r'^AS\d+$'

    # Check the input string against each pattern and return the type if a match is found
    if re.match(ip_pattern, input_str):
        return "ip"
    elif re.match(domain_pattern, input_str):
        return "domain"
    elif re.match(port_pattern, input_str):
        return "port"
    elif re.match(mac_pattern, input_str):
        return "mac"
    elif re.match(url_pattern, input_str):
        return "url"
    elif re.match(asn_pattern, input_str):
        return "asn"
    else:
        return "unknown"

# Prompt the user to enter the target
target = input("Enter IP, domain, port, MAC address, URL, or ASN: ")

# Call the function to identify the target type
target_type = target_input_type(target)

# Check if the target type is unknown or if the target is empty
if target_type == "unknown":
    print(f"Invalid input: {target}")
    exit(1)

if target == "":
    print("No target specified.")
    exit(1)
