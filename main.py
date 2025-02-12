from Assets import Configurations
from flask import Flask, jsonify, request
from pyngrok import ngrok, conf

task_no: str = None
app = Flask(__name__)

@app.route('/taskTrigger', methods=['GET'])
def taskTrigger():
    task = Configurations()
    trigger = task.triggerTask()
    if trigger:
        return jsonify({'message': 'Task triggered'}), 200
    return jsonify({'message': 'Trigger failed'}), 500

@app.route('/taskStatus', methods=['GET'])
def taskStatus():
    task_name = request.args.get('task_name')
    task = Configurations()
    status = task.checkStatus(task_name)
    if status:
        return jsonify({"message": "Task was successful"}), 200
    return jsonify({"message": "Task failed"}), 500

if __name__ == "__main__":
    conf.get_default().ngrok_path = "C:\\Users\\INKUBIL\\Downloads\\ngrok-v3-stable-windows-amd64\\ngrok.exe"
    conf.get_default().config_path = "ngrok.yml"
    public_url = ngrok.connect(5000)
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000\"".format(public_url))
    app.run()