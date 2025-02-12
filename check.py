import json
import requests

url: str = None
access_token: str = None
content_type: str = None
with open('tp01.json', 'r') as config:
    config_data = json.load(config)

    try:
        url = config_data["url"]
        access_token = config_data["access_token"]
        content_type = config_data["Content-Type"]
    except:
        print("Error, Key not found")

header = {
    'Authorization': str("Bearer " + str(access_token)),
    'Content-Type': content_type
}

response = requests.request("GET", url, headers=header)

if(response.status_code == 200):
    response_data = response.json()

    try:
        job = response_data.get("settings")
        print(job, end='\n\n')
    except:
        print("Error, Key not found")
    
    try:
        parameters = job["parameters"]
        print(parameters, end='\n\n')
    except:
        print("Key not found")
        
    try:
        for key_val in parameters:
            if(key_val['name'] == 'offset'):
                key_val['default'] = 100
                print(key_val['default'], end='\n\n')
    except:
        print("dict not found")
    
    print(job)
else:
    print(f"Error accessing the site.\nStatus: {response.status_code}")