def wildcard_to_netmask(wildcard):
    try:
        # Split the wildcard string into octets
        octets = wildcard.split('.')
        
        # Initialize an empty list to store the netmask octets
        netmask_octets = []
        
        # Iterate through the wildcard octets and convert to netmask
        for octet in octets:
            # Convert the octet to an integer
            octet_value = int(octet)
            
            # Calculate the netmask octet by subtracting the octet value from 255
            netmask_octet = 255 - octet_value
            
            # Append the netmask octet to the list
            netmask_octets.append(str(netmask_octet))
        
        # Join the netmask octets and return the subnet netmask
        subnet_netmask = '.'.join(netmask_octets)
        return subnet_netmask
    
    except ValueError:
        return "Invalid wildcard format"

# Example usage:
wildcard = "0.0.0.255"
subnet_netmask = wildcard_to_netmask(wildcard)
print("Subnet Netmask:", subnet_netmask)
