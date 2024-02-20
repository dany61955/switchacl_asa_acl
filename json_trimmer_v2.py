import json

def trim_json(input_file, output_file, attributes):
    with open(input_file, 'r') as f:
        data = json.load(f)

    trimmed_data = [{attr: entry[attr] for attr in attributes} for entry in data]

    with open(output_file, 'w') as f:
        json.dump(trimmed_data, f, indent=4)

if __name__ == "__main__":
    input_file = input("Enter input JSON file path: ")
    output_file = input("Enter output JSON file path: ")
    attributes_str = input("Enter attributes to keep (comma-separated): ")
    attributes = [attr.strip() for attr in attributes_str.split(',')]

    trim_json(input_file, output_file, attributes)
    print("Subset of JSON created successfully!")
