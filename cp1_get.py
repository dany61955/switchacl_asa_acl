#!/usr/bin/env python3
import paramiko
import sys
import json
import time
from getpass import getpass

class CheckPointSSH:
    def __init__(self, mds_ip, firewall_ip):
        self.mds_ip = mds_ip
        self.firewall_ip = firewall_ip
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.domain = None
        self.gateway_name = None
        self.policy_name = None

    def connect(self, username, password):
        """Establish SSH connection to MDS"""
        try:
            self.ssh.connect(self.mds_ip, username=username, password=password)
            return True
        except Exception as e:
            print(f"SSH connection failed: {str(e)}")
            return False

    def execute_command(self, command, timeout=30):
        """Execute command and return output"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
            return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
        except Exception as e:
            print(f"Command execution failed: {str(e)}")
            return None, None

    def login_to_cli(self):
        """Login to mgmt_cli"""
        stdout, stderr = self.execute_command('mgmt_cli login -f json')
        if stdout:
            try:
                response = json.loads(stdout)
                return response.get('sid')
            except json.JSONDecodeError:
                print("Failed to parse login response")
        return None

    def find_domain_and_policy(self, sid):
        """Find domain containing the firewall and its associated policy"""
        stdout, stderr = self.execute_command(f'mgmt_cli show domains --session-id {sid} -f json')
        if not stdout:
            return None, None

        try:
            domains = json.loads(stdout)['objects']
            for domain in domains:
                # Switch domain
                _, _ = self.execute_command(
                    f'mgmt_cli switch-domain name "{domain["name"]}" --session-id {sid}'
                )
                
                # Search for firewall in current domain
                stdout, _ = self.execute_command(
                    f'mgmt_cli show gateways-and-servers ip-only "{self.firewall_ip}" --session-id {sid} -f json'
                )
                
                if stdout:
                    try:
                        response = json.loads(stdout)
                        if response.get('objects'):
                            self.domain = domain["name"]
                            self.gateway_name = response['objects'][0]['name']
                            
                            # Get the policy package assigned to this gateway
                            stdout, _ = self.execute_command(
                                f'mgmt_cli show gateway name "{self.gateway_name}" --session-id {sid} -f json'
                            )
                            
                            if stdout:
                                gateway_details = json.loads(stdout)
                                if 'policy' in gateway_details:
                                    self.policy_name = gateway_details['policy']['name']
                                    return domain["name"], self.policy_name
                            
                            # If policy not found in gateway details, check all policies
                            stdout, _ = self.execute_command(
                                f'mgmt_cli show packages --session-id {sid} -f json'
                            )
                            
                            if stdout:
                                packages = json.loads(stdout)['objects']
                                for package in packages:
                                    if 'access-policy' in package:
                                        stdout, _ = self.execute_command(
                                            f'mgmt_cli show access-policy name "{package["name"]}" --session-id {sid} -f json'
                                        )
                                        if stdout:
                                            policy_details = json.loads(stdout)
                                            if 'installation-targets' in policy_details:
                                                targets = policy_details['installation-targets']
                                                if any(target['name'] == self.gateway_name for target in targets):
                                                    self.policy_name = package['name']
                                                    return domain["name"], self.policy_name
                    except json.JSONDecodeError:
                        continue
                        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing response: {str(e)}")
        
        return None, None

    def get_rulebase(self, sid):
        """Get the rulebase for the firewall"""
        if not self.domain or not self.policy_name:
            return None

        # Switch to correct domain
        _, _ = self.execute_command(
            f'mgmt_cli switch-domain name "{self.domain}" --session-id {sid}'
        )

        # Get access rulebase for the specific policy
        stdout, _ = self.execute_command(
            f'mgmt_cli show access-rulebase name "{self.policy_name}" --session-id {sid} -f json'
        )

        if stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                print("Failed to parse rulebase response")
        return None

    def logout(self, sid):
        """Logout from mgmt_cli"""
        self.execute_command(f'mgmt_cli logout --session-id {sid}')
        self.ssh.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python cp_fetch.py <mds_ip> <firewall_ip>")
        sys.exit(1)

    mds_ip = sys.argv[1]
    firewall_ip = sys.argv[2]

    cp = CheckPointSSH(mds_ip, firewall_ip)

    # Get credentials
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    if not cp.connect(username, password):
        print("Failed to connect to MDS")
        sys.exit(1)

    # Login to mgmt_cli
    sid = cp.login_to_cli()
    if not sid:
        print("Failed to login to mgmt_cli")
        cp.ssh.close()
        sys.exit(1)

    try:
        # Find domain and policy
        domain, policy = cp.find_domain_and_policy(sid)
        if not domain:
            print(f"Could not find firewall {firewall_ip} in any domain")
            sys.exit(1)

        print(f"Found firewall in domain: {domain}")
        print(f"Associated policy package: {policy}")
        print(f"Gateway name: {cp.gateway_name}")

        # Get rulebase
        rulebase = cp.get_rulebase(sid)
        if rulebase:
            print("\nRulebase:")
            print(json.dumps(rulebase, indent=2))
        else:
            print("Failed to fetch rulebase")

    finally:
        # Ensure we logout and close connection
        cp.logout(sid)

if __name__ == "__main__":
    main()
