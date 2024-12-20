import paramiko
import time

def ssh_connect(hostname, username, password, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Attempt connection
            print(f"Attempting to connect to {hostname}, attempt {retries + 1}")
            ssh.connect(hostname, username=username, password=password, timeout=10)
            
            print("Connection successful!")
            return ssh  # Return the SSH client object if successful

        except paramiko.AuthenticationException:
            print("Authentication failed. Check your credentials.")
            break  # No point in retrying if credentials are incorrect

        except paramiko.SSHException as e:
            print(f"SSH error: {e}. Retrying...")
            retries += 1
            time.sleep(5)  # Wait before retrying

        except Exception as e:
            print(f"Connection failed: {e}. Retrying...")
            retries += 1
            time.sleep(5)

    print("Max retries reached. Could not connect.")
    return None

# Usage example
hostname = "10.0.0.1"  # Replace with your Nexus IP
username = "admin"      # Replace with your username
password = "password"   # Replace with your password

ssh_client = ssh_connect(hostname, username, password)

if ssh_client:
    stdin, stdout, stderr = ssh_client.exec_command("show version")
    print(stdout.read().decode())
    ssh_client.close()
