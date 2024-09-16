import paramiko
import time
import getpass

# Function to read commands from a file
def read_commands_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to read the list of devices from a file
def read_device_list(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to send commands to a device via SSH and capture logs with prompt
def send_commands_to_device(hostname, username, password, commands):
    logs = []
    success = False

    try:
        # Initialize SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)
        
        # Open an interactive shell
        remote_conn = ssh.invoke_shell()
        time.sleep(1)
        
        # Getting the initial device prompt
        output = remote_conn.recv(65535).decode('utf-8')
        logs.append(f"{hostname}#")  # Initial prompt
        
        # Sending commands one by one
        for command in commands:
            remote_conn.send(command + "\n")
            time.sleep(2)  # Adjust the time delay if needed
            output = remote_conn.recv(65535).decode('utf-8')
            logs.append(f"{hostname}(config)#{command}")
        
        # After commands, get the final prompt
        logs.append(f"{hostname}#")
        success = True
    except Exception as e:
        logs.append(f"Error on {hostname}: {str(e)}")
    finally:
        ssh.close()
    
    return logs, success

# Function to apply SNMPv2 removal and SNMPv3 addition on a device
def configure_snmp(hostname, username, password, snmpv2_commands, snmpv3_commands):
    logs = []
    
    # Step 1: Remove SNMPv2
    logs.append(f"--- Removing SNMPv2 on {hostname} ---")
    snmpv2_logs, success_remove = send_commands_to_device(hostname, username, password, snmpv2_commands)
    logs.extend(snmpv2_logs)
    
    # Step 2: Add SNMPv3
    logs.append(f"--- Configuring SNMPv3 on {hostname} ---")
    snmpv3_logs, success_add = send_commands_to_device(hostname, username, password, snmpv3_commands)
    logs.extend(snmpv3_logs)
    
    return logs, success_remove and success_add

# Main function
def main():
    # File paths are direct relative paths
    snmpv2_file = "snmpv2_remove.txt"
    snmpv3_file = "snmpv3_add.txt"
    device_list_file = "input_device.txt"
    
    # Reading the commands and device list from files
    snmpv2_commands = read_commands_from_file(snmpv2_file)
    snmpv3_commands = read_commands_from_file(snmpv3_file)
    device_list = read_device_list(device_list_file)
    
    # Asking for device login credentials
    username = input("Enter device username: ")
    password = getpass.getpass("Enter device password: ")
    
    # Logs and report
    logs = []
    report = {
        "success": 0,
        "failed": 0
    }
    
    # Processing each device
    for device in device_list:
        logs.append(f"=== Configuring device {device} ===")
        device_logs, success = configure_snmp(device, username, password, snmpv2_commands, snmpv3_commands)
        logs.extend(device_logs)
        
        if success:
            report["success"] += 1
            logs.append(f"Device {device} configured successfully.\n")
        else:
            report["failed"] += 1
            logs.append(f"Device {device} configuration failed.\n")
    
    # Writing logs to file
    with open("snmp_configuration_logs.txt", "w") as log_file:
        log_file.write("\n".join(logs))
    
    # Printing the final report
    print(f"\n--- Configuration Report ---")
    print(f"Total Devices: {len(device_list)}")
    print(f"Successful Configurations: {report['success']}")
    print(f"Failed Configurations: {report['failed']}")
    print("\nLogs have been written to 'snmp_configuration_logs.txt'.")

if __name__ == "__main__":
    main()
