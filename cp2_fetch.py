import requests
from cp_mgmt_api_python_sdk import APIClient, APIClientArgs

# Disable warnings for unverified HTTPS
requests.packages.urllib3.disable_warnings()

def authenticate_mds(mds_ip, username, password):
    """Authenticate to MDS and get the session object."""
    client_args = APIClientArgs(server=mds_ip, unsafe=True)
    client = APIClient(client_args)
    login_response = client.login(username, password)
    if not login_response.success:
        raise Exception(f"Failed to log in to MDS: {login_response.error_message}")
    return client

def find_domain_for_firewall(client, firewall_ip):
    """Find the domain manager associated with the firewall."""
    response = client.api_call("show-domains", {"details-level": "full"})
    if not response.success:
        raise Exception(f"Failed to fetch domains: {response.error_message}")

    for domain in response.data.get("objects", []):
        domain_name = domain["name"]
        domain_uid = domain["uid"]

        # Switch to domain context
        switch_response = client.api_call("switch-to-domain", {"uid": domain_uid})
        if not switch_response.success:
            print(f"Failed to switch to domain {domain_name}: {switch_response.error_message}")
            continue

        # Check if the firewall exists in this domain
        firewall_response = client.api_call("show-host", {"name": firewall_ip})
        if firewall_response.success:
            return domain_name, domain_uid

    raise Exception(f"Firewall {firewall_ip} not found in any domain.")

def fetch_rulebase(client, firewall_ip):
    """Fetch the rulebase for the firewall."""
    response = client.api_call("show-access-rulebase", {"name": firewall_ip, "details-level": "full"})
    if not response.success:
        raise Exception(f"Failed to fetch rulebase: {response.error_message}")
    return response.data

def main():
    # Input variables
    mds_ip = input("Enter MDS IP: ")
    firewall_ip = input("Enter Firewall IP: ")
    username = input("Enter MDS Username: ")
    password = input("Enter MDS Password: ")

    try:
        # Authenticate to MDS
        client = authenticate_mds(mds_ip, username, password)

        # Find the domain for the firewall
        domain_name, domain_uid = find_domain_for_firewall(client, firewall_ip)
        print(f"Firewall {firewall_ip} is linked to domain: {domain_name}")

        # Switch to the domain and fetch rulebase
        client.api_call("switch-to-domain", {"uid": domain_uid})
        rulebase = fetch_rulebase(client, firewall_ip)

        # Display the rulebase
        print("Firewall Rulebase:")
        for rule in rulebase["rulebase"]:
            print(f"Rule {rule['rule-number']}: {rule['name']} (Action: {rule['action']})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'client' in locals():
            client.logout()

if __name__ == "__main__":
    main()
