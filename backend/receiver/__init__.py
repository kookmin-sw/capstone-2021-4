import os
from flask import Flask
from flask import request
import logging
import json

app = Flask(__name__)
app.debug = True
app.secret_key = os.environ.get("secret")

actions_permission = {
    "upload" : False,
    "delete" : False,
    "read" :False,
    "update": False
}

@app.route('/')
def main():
    return {
        
    }
    pass


@app.route('/request/<secret>/<action>/<set_value>') #set permission for file upload / other
def set_permission(secret, action):
    # accpet / decline
    if secret == app.secret_key:
        if set_value == "true":
            actions_permission[action] = True
        elif set_value == "false":
            actions_permission[action] = False
            
    else:
        return {
            
        }
    pass

@app.route('/run/upload_file')
def upload_file():
    # file upload code
    pass 


def syscommand(shell):
    output = ""
    import subprocess
    process = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE)
    
    for line in process.stdout:
        output += str(line.decode("utf-8")) + "<br>"
        print(line.decode("utf-8"))
        
    process.wait()
    return output
 
 
# get app status 
@app.route("/status/<secret>/<app>")
def status(secret, app):
    if sercet == app.secret_key:
        
        server_result = syscommand("docker ps -a  --filter name={} --format 'table {{.Status}}' | grep -v 'STATUS'".format(app))
        
        if server_result in "Exited":
            app_status = "stopped"
        elif server_result in "Running":
            app_status = "running"
        
        return {
            "service_name" : service, 
            "status" : app_status
        }
    else:
        return {}
    

   
@app.route('/run/<secret>/')
def index(secret):
    print(os.environ.get("secret"))
    if secret == app.secret_key:
        shell = request.args.get('shell')
        output = syscommand(shell)
        
        return {
            "result" : output,
            "statuscode" : process.returncode,
            "command" : shell
        }
        
    else:
        return {
            
        }
        