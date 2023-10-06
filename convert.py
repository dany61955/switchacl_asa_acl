import re
from ciscoconfparse import CiscoConfParse

# Input file containing the existing ACL with IP addresses
input_file = 'existing_acl.txt'

# Output file for the ACL with objects
output_file = 'acl_with_objects.txt'

# Object group name
object_group_name = 'MyObjectGroup'

# Create a CiscoConfParse object from the input file
parse = CiscoConfParse(input_file)

# Find all ACL entries
acl_entries = parse.find_objects('^access-list')

# Create a dictionary to store IP addresses and their associated object names
ip_to_object = {}

# Iterate through ACL entries and extract IP addresses
for entry in acl_entries:
    # Extract IP address and permission from the ACL entry
    match = re.match(r'access-list (\d+) (.*?) (.*?)$', entry.text)
    if match:
        acl_number = match.group(1)
        permission = match.group(2)
        ip_address = match.group(3)
        
        # Generate an object name for the IP address
        object_name = f"{object_group_name}-{acl_number}-{ip_address.replace('.', '-')}"
        
        # Store the IP address and its object name in the dictionary
        ip_to_object[ip_address] = object_name
        
        # Replace the ACL entry with an object group reference
        entry.text = f"object-group network {object_name}\n description {permission} ACL entry\n network-object host {ip_address}"

# Create an object group for the IP addresses
object_group_text = [f"object-group network {object_group_name}"]
for ip, object_name in ip_to_object.items():
    object_group_text.append(f" description IP address {ip}")
    object_group_text.append(f" network-object host {ip}")
object_group_text.append("exit")

# Save the modified configuration to the output file
with open(output_file, 'w') as f:
    f.write(parse.to_config())
    f.write('\n'.join(object_group_text))

print(f"ACL with objects saved to {output_file}")
