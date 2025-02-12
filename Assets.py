import json
import requests

class Configurations:

    __access_token: str = None
    __jobId: str = None
    __content_type: str = None
    __url: str = None

    def __init__(self) -> None:
        
        with open('config.json', 'r') as config:
            config_data = json.load(config)

            try:
                self.__access_token = config_data["access_token"]
                databricks_cluster = config_data["databricks_cluster"]
                self.__jobId = config_data["job_id"]
                self.__content_type = config_data["Content-Type"]
            except:
                print("Configuration Error, key not found")

            else:
                self.__url = str("https://" + str(databricks_cluster) + "/api/2.2/jobs/")
            
            print(self.__url)
    
    def __del__(self) -> None:
        pass

    def checkStatus(self, task_name: str) -> str:
        
        offset: int = None
        checkTask: int = None
        with open('config.json', 'r') as config:
            config_data = json.load(config)
            
            try:
                task_names = config_data["task_name"]
            except:
                print("Key error, task_name not found")
            
            else:
                offset = task_names[task_name]
                checkTask = offset-1
        
        url = str(self.__url + "/runs/list?job_id=" + self.__jobId)

        header = {
            'Authorization': self.__access_token,
            'Content-Type': self.__content_type
        }

        response = requests.request("GET", url, headers=header)

        runId: str = None
        if(response.status_code == 200):
            response_data = response.json()

            try:
                run = response_data.get('runs', [])

                runId = run[0]['run_id']
            except:
                print("runs not found for the given job")
        
        task: str = None
        if(runId):
            url = str(self.__url + "runs/get?run_id=" + runId)

            run_response = requests.request("GET", url, headers=header)

            if(run_response.status_code == 200):
                run_response_data = run_response.json()
                
                try:
                    task = run_response_data['tasks'][checkTask]['state']['result_state']
                except:
                    print("key error, task status cannot be retrieved")
        
        check: bool = False
        if(task == "SUCCESS"):
            check = self.triggerTask()
        
        if(check):
            return True
        
        return False

    def triggerTask(self):

        offset: int = None
        with open('config.json', 'r') as config:
            config_data = json.load(config)

            try:
                offset = config_data['offset']
                tasks_id = config_data['tasks_id']
            except:
                print("Key error, offset key not found")
        
        if(offset):
            offset+=1
            config_data['offset'] = offset
        
        with open('config.json', 'w') as config:
            json.dump(config_data, config, indent=4)
        
        url = str(self.__url + "get?=" + self.__jobId)

        header = {
            'Authorization': str("Bearer " + self.__access_token),
            'Content-Type': self.__content_type
        }

        response = requests.request("GET", url,headers=header)

        if(response.status_code == 200):
            
            response_data = response.json()

            try:
                job = response_data.get('settings')
            except:
                print("settings field not found in the job")

            try:
                parameters = job['parameters']
            except:
                print("parameters field not found in the job")

            try:
                for key_val in parameters:
                    if(key_val["name"] == "offset"):
                        key_val['default'] = tasks_id[offset]

            except:
                print("parameters dictionary not found in the response") 

            url = str(self.__url + "update")

            updated_job_settings = {
                'job_id': self.__jobId,
                'new_settings': job
            }

            update_response = requests.request("POST", url, headers=header, json=updated_job_settings)

            if(update_response.status_code == 200):
                return True

            else:
                print("Error updating the parameters")

        return False

        
