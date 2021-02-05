from flask import render_template, Blueprint, request, redirect, url_for,  flash, Markup
from flask_jsonpify import jsonify
from flask_login import current_user, login_required
from project import db
from project import app
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityRule, NetInterface
import boto3
import os
from .forms import CloudForm, EditCloudForm
from .utils import back_ec2_delete_vpc,back_ec2_create_vpc, back_ec2_create_net_interface, back_ec2_delete_net_interface, back_ec2_create_subnet, back_ec2_delete_subnet, back_ec2_create_int_gateway, back_ec2_delete_int_gateway, back_ec2_int_gateway_attach_vpc, back_ec2_int_gateway_detach_vpc, back_ec2_create_security_group, find_route_table, route_table_init, check_environment, set_default_security_group, create_environment, back_ec2_create_ec2, back_ec2_instance_detail, delete_ec2
 
from sqlalchemy import or_, and_
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime

import time  
# # CONFIG
cloud_blueprint = Blueprint('cloud', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 
 
import json


class AlchemyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o.__class__, DeclarativeMeta):
            data = {}
            fields = o.__json__() if hasattr(o, '__json__') else dir(o)
            for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
                value = o.__getattribute__(field)
                try:
                    json.dumps(value)
                    data[field] = value
                except TypeError:
                    data[field] = None
            return data
        return json.JSONEncoder.default(self, o)


@cloud_blueprint.route('/list', methods=['GET'])
@login_required
def all_clouds():
    # job = q.enqueue(background_task, request.args.get("n"))
    # Check Status, IPAddr, Status
    cloud_lists = db.session.query(Plan, Cloud,Oslist).join(Cloud).filter(Cloud.user_id == current_user.id,Cloud.os == Oslist.id).all()
    rest = request.args.get("rest") 
    json_object = json.dumps(cloud_lists, cls=AlchemyEncoder)
    if rest == "true":
        return json_object 
    else:
        return render_template('all_clouds.html', cloud=cloud_lists)

@cloud_blueprint.route('/reboot/<cloud_id>', methods=['POST'])
@login_required
def reboot_instance(instance_id):
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(and_(
        Cloud.user_id == current_user.id,
        Cloud.id == cloud_id
    )).first()
    if cloud_with_user is not None:
        try:
            response = ec2.reboot_instances(InstanceIds=[instance_id], DryRun=False)
            print('Success', response)
            return "Success"
        except ClientError as e:
            print('Error', e)

@cloud_blueprint.route('/delete/<instance_id>')
@login_required
def delete_cloud(instance_id):
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(and_(
        Cloud.user_id == current_user.id,
        Cloud.id == instance_id
    )).first()
    if cloud_with_user is not None:
        try:
            aws_instance_id = cloud_with_user.Cloud.aws_instance_id
            print("[Debug] - {}".format(instance_id))
            response = delete_ec2(cloud_with_user.Cloud.aws_instance_id)
            now = datetime.now()
            cloud = Cloud.query.filter_by(aws_instance_id=aws_instance_id).first()
            cloud.status = "Terminated"
            cloud.deleted_at = now.strftime("%Y-%m-%d %H:%M:%S")
            db.session.add(cloud)
            db.session.commit()
            flash('{} was Terminated.'.format(cloud.hostname), 'success')
        except Exception as e:
            db.session.rollback()
            message = Markup("<strong>Error!</strong> Eroror{} ".format(e))

            flash(message, 'danger')
    
    return redirect(url_for('cloud.all_clouds'))
            
    

@cloud_blueprint.route("/update", methods=['GET', 'POST'])
@login_required
def update_cloud():
    pass

@cloud_blueprint.route("/detail/<cloud_id>", methods=['GET'])
@login_required
def detail(cloud_id):
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(Cloud.id == cloud_id).first()
    if cloud_with_user is not None:
        if current_user.is_authenticated and cloud_with_user.Cloud.user_id == current_user.id:
            # show cloud detail
            # print(cloud_with_user.Cloud.aws_instance_id )
            aws_instance = cloud_with_user.Cloud.aws_instance_id 
            cloudid = cloud_with_user.Cloud.id
            response = back_ec2_instance_detail(aws_instance)
            return render_template('cloud_detail.html', cloud=response)
        else:
            message = Markup("<strong>잘못된 접근입니다.</strong>  ")
            flash(message, 'danger') 
    else:
        message = Markup("<strong>잘못된 접근입니다.</strong>  ")
        flash(message, 'danger')
    
    return render_template('cloud_detail.html')




@cloud_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_cloud():
    form = CloudForm(request.form)
    plans = Plan.query.all()
    os_list = Oslist.query.all() 
    keypair_list = db.session.query(Keypair.id, Keypair.name).filter(Keypair.user_id == current_user.id )
    sec_list = db.session.query(SecurityRule.id,SecurityRule.sec_group_id).filter(SecurityRule.user_id == current_user.id)

    if request.method == 'POST': 
        if form.validate_on_submit(): 
            try:
                plan_id = form.data["plan"]
                sec_id = form.data["secgroup"]
                get_sec_id = db.session.query(SecurityRule.sec_group_id).filter(SecurityRule.id == sec_id).scalar()

                get_aws_plan = db.session.query(Plan.aws_plan,Plan.ssd, Plan.iops).filter(Plan.id == plan_id)[0]
                param_plan = get_aws_plan[0]
                param_ssd = get_aws_plan[1]
                param_iops = get_aws_plan[2]
                vpc_info = db.session.query(VPC.vpc_id, VPC.inter_gw_id, VPC.default_subnet_id, VPC.default_sec_id, VPC.id).filter(VPC.user_id == current_user.id)[0]
                aws_image_id = db.session.query(Oslist.aws_image_id).filter(Oslist.id == form.data["os"]).scalar()
                vpc_id = vpc_info[4]
                vpc_default_subnetid = vpc_info[2]
                vpc_default_secid = vpc_info[3]
                keypair_id = form.data["keypair"]

                if check_environment(current_user.id) == True: 
                    get_keypair = db.session.query(Keypair.name).filter(Keypair.id == keypair_id).scalar()
                    keypairname_formatted = "{}_{}".format( current_user.email , get_keypair) 
                    # net_interface = back_ec2_create_net_interface(vpc_default_subnetid) 
                    # net_interface_id = net_interface["NetworkInterface"]["NetworkInterfaceId"]
                    # new_interface = NetInterface(net_interface_id, vpc_default_subnetid)
                    # db.session.add(new_interface)
                    
                    
                    # result = back_ec2_create_ec2( )
                    # instance_id = result["Instances"][0]["InstanceId"]
                    new_cloud = Cloud(form.data["Hostname"], form.data["plan"], current_user.id, form.data["os"], "Queued", "Requesting", "Seoul" , keypair_id , vpc_id, "Requesting")
                    db.session.add(new_cloud) 
                    db.session.flush() 
                    db.session.refresh(new_cloud)
                    assigned_id = new_cloud.id
                    db.session.commit()

                    parameter = {
                        "plan" : param_plan,
                        "iops" : param_iops,
                        "ssd" : param_ssd,
                        "subnetid" : vpc_default_subnetid,
                        "keypair" : keypairname_formatted,
                        "security-group-id" : [get_sec_id],
                        "cloudid" : assigned_id
                    }
                    
                    job = q.enqueue(back_ec2_create_ec2, parameter)
                    
                    print("Task ({}) added to queue at {}".format(job.id, job.enqueued_at))
                    
                else:
                    raise Exception("관리자에게 문의해 주세요.")

                
                # 2. DB 에 기록..
                # new_cloud = Cloud(form.name.data, form.
                message = Markup(
                    "<strong>Well done!</strong> Cloud Deploy Request successfully!")
                flash(message, 'success')                   
                return redirect(url_for('cloud.all_clouds'))
            except Exception as mesg:
                db.session.rollback()
                # 조금있다가 생각
                # if vpc_id:
                #     print("vpcId : {} ".format(vpc_id))
                #     vpc_select = db.session.query(VPC.vpc_id).filter(VPC.id == vpc_id)
                #     back_ec2_delete_vpc(vpc_select)
                # SDK rollback implement need
                message = Markup(
                    "<strong>내부 API 에러{}".format(mesg))
                flash(message, 'danger')
    else:
        print("GET")
    
    return render_template('add_cloud.html', form=form, planlist = plans, oslist = os_list, keypair = keypair_list, secgroup=sec_list)

