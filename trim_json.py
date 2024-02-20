import json

def trim_json(input_json):
    # Load the input JSON
    data = json.loads(input_json)
    
    # Define criteria for trimming
    criteria = ["name", "age", "email"]  # Example criteria
    
    # Create a subset of the output JSON based on the criteria
    output_json = {key: data[key] for key in criteria if key in data}
    
    return json.dumps(output_json, indent=4)

# Example JSON input
input_json = '''
{
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com",
    "phone": "1234567890"
}
'''

# Trim the input JSON and print the subset output JSON
output_json = trim_json(input_json)
print(output_json)
