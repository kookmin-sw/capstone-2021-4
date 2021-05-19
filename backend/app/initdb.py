from project import app,db
from project.models import Oslist, Plan, User, CloudAppCommand
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

def app_add():
    flask = Oslist('flask', 'ami-04f79737f53352f18')
    db.session.add(flask)
    db.session.commit()
    
#flask script
def add_app_script():

    flask_update_script = """
    cd /home/ec2-user/public_flask
    """
    appcommand1 = CloudAppCommand("update", flask_update_script, 1, 1, "script" )
    flask_update_script2 = """
    docker+build+-t+flaskapp%3A%24%28docker+images+%7C+awk+%27%28%241+%3D%3D+%22flaskapp%22%29+%7Bprint+%242+%2B%3D+.01%3B+exit%7D%27%29+%2Fhome%2Fec2-user%2Fpublic_flask%2F
    """
    appcommand2 = CloudAppCommand("update", flask_update_script2, 1, 2, "script" )
    
    flask_update_script3 = """
    docker rm -f {app_register}
    """
    appcommand3 = CloudAppCommand("update", flask_update_script3, 1, 3, "script" )
    
    flask_update_script4 = """docker+run+-itd+-p+{app_port}%3A80+--name+{app_register}+flaskapp%3A%24%28docker+images+%7C+awk+%27%28%241+%3D%3D+%22flaskapp%22%29+%7Bprint+%242+%2B%3D+.0%3B+exit%7D%27%29"""
    appcommand4 = CloudAppCommand("update", flask_update_script4, 1, 4, "script" )
    
    
    db.session.add(appcommand1)
    db.session.add(appcommand2)
    db.session.add(appcommand3)
    db.session.add(appcommand4)
    db.session.commit()
    
