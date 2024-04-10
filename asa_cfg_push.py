import paramiko
import re

def read_config(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def push_config(hostname, username, password, enable_password, config_lines):
    try:
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)

        # Create shell
        ssh_shell = ssh_client.invoke_shell()

        # Send enable command
        ssh_shell.send("enable\n")
        ssh_shell.send(enable_password + "\n")
        output = ssh_shell.recv(65535).decode('ascii')

        # Check if enable mode is reached
        if re.search(r'\S+#', output):
            for line in config_lines:
                ssh_shell.send(line)
                output = ssh_shell.recv(65535).decode('ascii')
                # Check for errors
                if re.search(r'%\sError:', output):
                    print(f"Error executing line: {line.strip()}")
                else:
                    print(f"Successfully executed line: {line.strip()}")
        else:
            print("Failed to enter enable mode.")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        ssh_client.close()

# Configuration
config_file = 'config.txt'
hostname = 'your_asa_ip'
username = 'your_username'
password = 'your_password'
enable_password = 'your_enable_password'

# Read config file
config_lines = read_config(config_file)

# Push configuration
push_config(hostname, username, password, enable_password, config_lines)
