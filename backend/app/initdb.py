from project import app,db
from project.models import Oslist, Plan, User, CloudApp
#plan
# id: int
# plan_name: str
# aws_plan: str
# core: int
# ram: int
# traffic:int
# ssd: int
# iops: int
def plan_add(): 
    sample_plan = Plan('m2.small', 't3.small', 1, 2048, 2000, 40, 4000)
    sample_plan2 = Plan('m3.medium', 't3.medium', 4096, 4000, 2048, 60, 4500)
    sample_plan3 = Plan('m3.big', 't3.xlarge', 4, 16384, 6000, 100, 5000)
    sample_plan4 = Plan('m4.large', 't3.2xlarge', 8, 32768, 8000, 100, 5500)
    db.session.add(sample_plan)
    db.session.add(sample_plan2)
    db.session.add(sample_plan3)
    db.session.add(sample_plan4)
    db.session.commit()


def admin_add():
# Admin User ad
    new_user = User('admin@testtest.com', '123!asdf')
    new_user.authenticated = True
    new_user.role ='admin'
    
    db.session.add(new_user)

def os_add():
    sample_os = Oslist('ubuntu20.04', 'ami-067abcae434ee508b')
    sample_os2  = Oslist('amazonLinux', 'ami-09282971cf2faa4c9')
    
    db.session.add(sample_os)
    db.session.add(sample_os2)
    
    db.session.commit()

#flask script
def add_app_script():


    flask_update_script = """
    cd /home/ec2-user/public_flask
    git add .
    git commit -m "Update"
    docker build -t flaskapp:$(docker images | awk '($1 == "flaskapp") {print $2 += .01; exit}') .
    docker rm -f green
    docker run -itd --name green flaskapp:$(docker images | awk '($1 == "flaskapp") {print $2 += .01; exit}')
    """
 
    pythonapp = CloudApp("Python", "python:3.6.13-slim", "8080", 1)
    db.session.add(pythonapp)
    db.session.commit()
    
    # appcommand = CloudAppCommand("deplo", pythonapp_script, 0, pythonapp.id, "script" )
    appcommand = CloudAppCommand("deploy", pythonapp_script, 0, pythonapp.id, "script" )
    appcommand = CloudAppCommand("update", pythonapp_script, 0, pythonapp.id, "script" )
    appcommand = CloudAppCommand("rollback", pythonapp_script, 0, pythonapp.id, "script" )
    

    pass
