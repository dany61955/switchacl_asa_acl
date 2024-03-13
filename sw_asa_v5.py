import ipaddress

def generate_object_name(ip, is_host):
    if is_host:
        return "HST_" + ip
    else:
        network = ipaddress.ip_network(ip, strict=False)
        return "NET_" + str(network.network_address) + "_" + str(network.netmask)

def convert_acl_line_to_asa(line):
    parts = line.split()
    if parts[1] == 'ip' and parts[2] == 'host':
        source_ip = parts[3]
        source_object = generate_object_name(source_ip, True)
        dest_ip = parts[5]
        dest_object = generate_object_name(dest_ip, True)
    elif parts[1] == 'ip':
        source_ip = parts[2]
        source_mask = parts[3]
        source_object = generate_object_name(source_ip + "/" + source_mask, False)
        dest_ip = parts[4]
        dest_mask = parts[5]
        dest_object = generate_object_name(dest_ip + "/" + dest_mask, False)
    else:
        raise ValueError("Unsupported ACL format")
    
    return f"access-list acl_name extended permit ip object {source_object} object {dest_object}\n" \
           f"object network {source_object}\n" \
           f" { 'host ' if '/' not in source_ip else '' }{source_ip}\n" \
           f"object network {dest_object}\n" \
           f" { 'host ' if '/' not in dest_ip else '' }{dest_ip}\n"

# Example ACL lines
acl_lines = [
    "permit ip host 192.168.1.1 host 10.0.0.1",
    "permit ip host 192.168.1.1 10.0.0.0 255.255.255.0",
    "permit ip 192.168.1.0 255.255.255.0 10.0.0.0 255.255.255.0",
    "permit ip 192.168.1.0 255.255.255.0 host 10.0.0.1"
]

asa_acl_lines = ""
for line in acl_lines:
    asa_acl_lines += convert_acl_line_to_asa(line)

print(asa_acl_lines)
