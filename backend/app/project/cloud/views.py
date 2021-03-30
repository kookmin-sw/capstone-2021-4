from flask import render_template, Blueprint, request, redirect, url_for,  flash, Markup, jsonify, abort
from flask_login import current_user, login_required
from project import db
from project import app
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityGroup, NetInterface, Balance
import boto3
import os
from .forms import CloudForm, EditCloudForm
from .utils import *
 
from sqlalchemy import or_, and_
from sqlalchemy.ext.declarative import DeclarativeMeta
import datetime

import time  
from dataclasses import dataclass
# # CONFIG
cloud_blueprint = Blueprint('cloud', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 

import json

def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

@cloud_blueprint.route('/list', methods=['GET'])
@login_required
def all_clouds():
    # job = q.enqueue(background_task, request.args.get("n"))
    # Check Status, IPAddr, Status
    cloud_lists = db.session.query(Plan, Cloud,Oslist).join(Cloud).filter(Cloud.user_id == current_user.id,Cloud.os == Oslist.id).all()
    rest = request.args.get("rest")   
    if rest == "true":  
        # json_object = json.dumps(cloud_lists, cls=AlchemyEncoder)
        return cloud_lists
    else:
        return render_template('cloud/list.html', cloud=cloud_lists)

@cloud_blueprint.route('/reboot/<instance_id>', methods=['GET'])
@login_required
def reboot_instance(instance_id):
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(and_(
        Cloud.user_id == current_user.id,
        Cloud.id == instance_id
    )).first()
    if cloud_with_user is not None:
        # try:
        response = reboot_instances(cloud_with_user.Cloud.aws_instance_id)
        flash('Rebooted.' , 'success')
        # except Exception as e: 
        #     message = Markup("<strong>Error!</strong> Eroror{} ".format(e)) 
        #     flash(e, 'danger')

    return redirect(url_for('cloud.all_clouds'))

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
            import datetime
            cloud = Cloud.query.filter_by(aws_instance_id=aws_instance_id).first()
            cloud_id = cloud.id
            now = datetime.datetime.now()
            netInterface = NetInterface.query.filter_by(cloud_id=cloud_id).first()
            if netInterface is not None:
                netInterface.detached_at = now
                netInterface.deleted_at = now

            cloud.status = "Terminated" 
            cloud.deleted_at = now
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
    cwclient = boto3.client(service_name='cloudwatch') 
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(Cloud.id == cloud_id).first()
    if cloud_with_user is not None:
        if current_user.is_authenticated and cloud_with_user.Cloud.user_id == current_user.id:
            # show cloud detail
            # print(cloud_with_user.Cloud.aws_instance_id )
            aws_instance = cloud_with_user.Cloud.aws_instance_id 
            cloudid = cloud_with_user.Cloud.id
            response = back_ec2_instance_detail(aws_instance)
            screenshot = get_console_screenshot(aws_instance)
            output = get_console_output(aws_instance)
            

            from datetime import datetime, timedelta
            today = datetime.today()
            datem = datetime(today.year, today.month, 1)  #1일마다 초기화
            cw_response = cwclient.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkOut',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': aws_instance
                    },
                ],  
                StartTime=datem,
                EndTime=datetime.now(),
                Period=86400,
                Statistics=[
                    'Sum'
                ],  
            )
            print(datem)

            print(cw_response)

            if len(cw_response["Datapoints"]) > 0:
                plan_data = db.session.query(Plan).filter(Plan.id == cloud_with_user.Cloud.plan_id).first()
                total_plan_traffic = plan_data.traffic
                
                from hurry.filesize import size
                outbound_traffic = "{} / {} MB".format( humansize(cw_response["Datapoints"][0]["Sum"]) , total_plan_traffic)
                
            else:
                outbound_traffic = "none"
             
            return render_template('cloud/detail.html', cloud=response, screenshot=screenshot, output=output, traffic=outbound_traffic)
        else:
            message = Markup("<strong>잘못된 접근입니다.</strong>  ")
            flash(message, 'danger') 
    else:
        message = Markup("<strong>잘못된 접근입니다.</strong>  ")
        flash(message, 'danger')
    
    return redirect(url_for('home'))

@cloud_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_cloud():
    form = CloudForm(request.form)
    plans = Plan.query.all()
    os_list = Oslist.query.all() 
    keypair_list = db.session.query(Keypair.id, Keypair.name).filter(Keypair.user_id == current_user.id )
    sec_list = db.session.query(SecurityGroup).filter(SecurityGroup.user_id == current_user.id)
    
    credit_sum = db.session.query(Balance.balance).filter_by(user_id=current_user.id).scalar()
    
    if credit_sum < 1: # 관리자 승인된 크레딧을 1원이라도 충전하지 않았을 경우
        print("크레딧이 없습니다 같은 메세지")
        abort(403)
    
    if request.method == 'POST': 
        if form.validate_on_submit(): 
            try:
                plan_id = form.data["plan"]
                sec_id = form.data["secgroup"]
                get_sec_id = db.session.query(SecurityGroup.sec_group_id).filter(SecurityGroup.id == sec_id).scalar()

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
                    # 기존 키 페어 찾아서 클라우드에 반영
                    get_keypair = db.session.query(Keypair.name, Keypair.keytoken).filter(Keypair.id == keypair_id).first()
                    keypairname_formatted = "{}_{}".format( get_keypair.keytoken , get_keypair.name) 

                    # DB에 기록
                    new_cloud = Cloud(form.data["Hostname"], form.data["plan"], current_user.id, form.data["os"], "Queued", "Requesting", "Seoul" , keypair_id , vpc_id, "Requesting")
                    db.session.add(new_cloud) 
                    db.session.flush()
                    db.session.refresh(new_cloud)

                    assigned_id = new_cloud.id
                    print("AssignedId : {}".format(assigned_id))
                    db.session.commit()

                    parameter = {
                        "plan" : param_plan,
                        "iops" : param_iops,
                        "ssd" : param_ssd,
                        "os" : aws_image_id,
                        "subnetid" : vpc_default_subnetid,
                        "keypair" : keypairname_formatted,
                        "security-group-id" : [get_sec_id],
                        "cloudid" : assigned_id,
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
    
    return render_template('cloud/add.html', form=form, planlist = plans, oslist = os_list, keypair = keypair_list, secgroup=sec_list)

