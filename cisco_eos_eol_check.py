import csv
import requests

# Replace with your Cisco API access token
API_TOKEN = 'YOUR_ACCESS_TOKEN'

def check_eol_eos(part_number):
    url = f"https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID/{part_number}?responseencoding=json"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
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
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_reader = csv.reader(infile)
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['Part/Model', 'EOL', 'EOS'])

        for row in csv_reader:
            part_number = row[0]
            eol, eos = check_eol_eos(part_number)
            csv_writer.writerow([part_number, eol, eos])

if __name__ == "__main__":
    input_file = 'input_parts.csv'
    output_file = 'eol_eos_status.csv'
    main(input_file, output_file)
