
#Create a devices.txt File: Add your devices in the following format:
#192.168.1.1,admin,password,cisco_ios
#192.168.1.2,admin,password,cisco_ios
#192.168.1.3,admin,password,cisco_nxos



import logging
from netmiko import ConnectHandler
import time
import csv

# Define a logging filter to add the hostname dynamically
class HostnameFilter(logging.Filter):
    def __init__(self, hostname):
        super().__init__()
        self.hostname = hostname

    def filter(self, record):
        record.hostname = self.hostname
        return True

# Set up logging with UTC timestamps
def setup_logging(hostname):
    logger = logging.getLogger("netmiko")
    logger.setLevel(logging.DEBUG)
    
    # Define a log format with hostname and UTC timestamp
    log_format = "%(asctime)s [%(hostname)s] %(levelname)s: %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Set formatter to use UTC time
    formatter.converter = time.gmtime  # Converts to UTC
    
    # Create a file handler
    file_handler = logging.FileHandler("netmiko_debug.log")
    file_handler.setFormatter(formatter)
    
    # Add the custom filter with hostname
    file_handler.addFilter(HostnameFilter(hostname))
    
    # Add the handler to the logger
    logger.addHandler(file_handler)

# Function to process a single device
def process_device(device_info):
    host, username, password, device_type = device_info
    device = {
        "device_type": device_type.strip(),
        "host": host.strip(),
        "username": username.strip(),
        "password": password.strip(),
    }

    # Set up logging for this device
    setup_logging(device["host"])

    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command("show version")
            print(f"Output for {device['host']}:\n{output}")
    except Exception as e:
        logging.error(f"Failed to process {device['host']}: {e}")

# Main function to read devices from file and process them
def main(device_file):
    with open(device_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # Skip empty lines
                process_device(row)

if __name__ == "__main__":
    # Specify the path to your devices file
    devices_file = "devices.txt"
    main(devices_file)
