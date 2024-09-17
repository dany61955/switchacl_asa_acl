import paramiko
import time
import getpass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to read commands from a file
def read_commands_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to read the list of devices from a file
def read_device_list(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to send configuration commands to a device via SSH
def send_config_commands_to_device(hostname, username, password, commands):
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
        
        # Get the device prompt (e.g., "hostname#")
        remote_conn.send("\n")
        time.sleep(1)
        output = remote_conn.recv(65535).decode('utf-8')
        logs.append(output.strip())
        
        # Enter global configuration mode
        remote_conn.send("configure terminal\n")
        time.sleep(1)
        output = remote_conn.recv(65535).decode('utf-8').strip()
        logs.append(output)
        
        # Send configuration commands one by one
        for command in commands:
            remote_conn.send(command + "\n")
            time.sleep(2)  # Adjust the delay if needed
            output = remote_conn.recv(65535).decode('utf-8').strip()
            logs.append(output)
        
        # Exit configuration mode
        remote_conn.send("end\n")
        time.sleep(1)
        output = remote_conn.recv(65535).decode('utf-8').strip()
        logs.append(output)
        
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
    snmpv2_logs, success_remove = send_config_commands_to_device(hostname, username, password, snmpv2_commands)
    logs.extend(snmpv2_logs)
    
    # Step 2: Add SNMPv3
    logs.append(f"--- Configuring SNMPv3 on {hostname} ---")
    snmpv3_logs, success_add = send_config_commands_to_device(hostname, username, password, snmpv3_commands)
    logs.extend(snmpv3_logs)
    
    return logs, success_remove and success_add

# Function to handle device configuration in parallel
def configure_device_in_parallel(device, username, password, snmpv2_commands, snmpv3_commands):
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs = [f"=== Configuring device {device} ===", f"Start time: {start_time}"]
    
    device_logs, success = configure_snmp(device, username, password, snmpv2_commands, snmpv3_commands)
    logs.extend(device_logs)
    
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs.append(f"End time: {end_time}")
    
    if success:
        logs.append(f"Device {device} configured successfully.\n")
    else:
        logs.append(f"Device {device} configuration failed.\n")
    
    return logs, success

# Main function
def main():
    # File paths are now direct relative paths
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
    
    # Set the parallel processing count as a variable
    parallel_count = int(input("Enter the number of devices to configure in parallel: "))
    
    # Logs and report
    logs = []
    report = {
        "success": 0,
        "failed": 0
    }
    
    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=parallel_count) as executor:
        future_to_device = {executor.submit(configure_device_in_parallel, device, username, password, snmpv2_commands, snmpv3_commands): device for device in device_list}
        
        for future in as_completed(future_to_device):
            device = future_to_device[future]
            try:
                device_logs, success = future.result()
                logs.extend(device_logs)
                
                if success:
                    report["success"] += 1
                else:
                    report["failed"] += 1
            except Exception as exc:
                logs.append(f"Error configuring {device}: {exc}")
    
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
