import requests
import json

with open("tp01.json", 'r') as config:

    config_data = json.load(config)
    url = config_data["url3"]
    access_token = config_data["access_token"]
    content_type = config_data["Content-Type"]
    runId = config_data["runId"]

    url = str(url + runId)

header = {
    'Authorization': str("Bearer " + access_token),
    'Content-Type': content_type
}

response = requests.request("GET", url, headers=header)

if(response.status_code == 200):
    response_data = response.json()
    print(response_data['tasks'][3])

else:
    print(f"Error: {response.status_code}")