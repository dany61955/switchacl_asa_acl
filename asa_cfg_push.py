import paramiko

def read_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config_lines = file.readlines()
        return config_lines
    except FileNotFoundError:
        print("File not found!")
        return None

def push_config_to_asa(hostname, username, password, config_lines):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, password=password, timeout=10)
        
        remote_conn = ssh_client.invoke_shell()
        output = remote_conn.recv(65535)
        print(output.decode('utf-8'))
        
        for line in config_lines:
            remote_conn.send(line)
            output = remote_conn.recv(65535)
            print(output.decode('utf-8'))
        
        ssh_client.close()
        print("Configuration successfully applied to ASA.")
    except paramiko.AuthenticationException:
        print("Authentication failed!")
    except paramiko.SSHException as ssh_err:
        print(f"SSH error: {ssh_err}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace these values with your ASA's hostname/IP, SSH credentials, and config file path
    hostname = "your_asa_hostname_or_ip"
    username = "your_username"
    password = "your_password"
    config_file_path = "config.txt"

    config_lines = read_config(config_file_path)
    if config_lines:
        push_config_to_asa(hostname, username, password, config_lines)
    else:
        print("Failed to read configuration file.")
