import ipaddress

def ip_subnet_to_cidr(ip_address, subnet_mask):
    # Concatenate the IP address and subnet mask
    ip_cidr = ip_address + '/' + subnet_mask
    
    try:
        # Validate and convert the IP address with subnet to IPv4Network object
        subnet = ipaddress.IPv4Network(ip_cidr, strict=False)
        return str(subnet)
    except ValueError as e:
        return "Error: " + str(e)

def main():
    ip_address = input("Enter IP Address: ")
    subnet_mask = input("Enter Subnet Mask: ")

    cidr_notation = ip_subnet_to_cidr(ip_address, subnet_mask)
    
    # Extract the CIDR notation from the result
    cidr_components = cidr_notation.split('/')
    ip_cidr = cidr_components[0] + '_' + cidr_components[1]
    
    print("IP Address with CIDR:", ip_cidr)

if __name__ == "__main__":
    main()
