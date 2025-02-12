import json
import requests

url: str = None
access_token: str = None
content_type: str = None
with open('tp01.json', 'r') as config:
    config_data = json.load(config)

    try:
        url = config_data["url2"]
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

    runs = response_data.get('runs', [])

    try:
        print(runs[0]['run_id'])
    except:
        print("runs not found")
else:
    print(f"Error accessing the site.\nStatus: {response.status_code}")