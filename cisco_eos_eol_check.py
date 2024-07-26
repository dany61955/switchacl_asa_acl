import requests
import csv

client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
token_url = 'https://cloudsso.cisco.com/as/token.oauth2'
api_base_url = 'https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID'

def get_access_token(client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json().get('access_token')

def check_eol_eos(part_number, token):
    url = f"{api_base_url}/{part_number}?responseencoding=json"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        eol_status = data['EOXRecord'][0].get('EndOfLifeAnnouncementDate', {}).get('value', 'N/A')
        eos_status = data['EOXRecord'][0].get('EndOfServiceContractRenewal', {}).get('value', 'N/A')
        return f"Yes - dateEOL : {eol_status}", f"Yes - dateEOS : {eos_status}"
    else:
        return 'No', 'No'

def main(input_file, output_file):
    token = get_access_token(client_id, client_secret)
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_reader = csv.reader(infile)
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['Part/Model', 'EOL', 'EOS'])

        for row in csv_reader:
            part_number = row[0]
            eol, eos = check_eol_eos(part_number, token)
            csv_writer.writerow([part_number, eol, eos])

if __name__ == "__main__":
    input_file = 'input_parts.csv'
    output_file = 'eol_eos_status.csv'
    main(input_file, output_file)
