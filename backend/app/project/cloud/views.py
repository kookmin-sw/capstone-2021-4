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

from flask import send_file
import io

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

# def get_file_list(cloud_id):
#     pass

# def delete_file(path):
#     pass

# def update_file(path, to_filename):
#     pass





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

@cloud_blueprint.route('/deploy/<cloud_id>/<app_id>')
@login_required
def deploy_app( cloud_id, app_id ):
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(and_(
        Cloud.user_id == current_user.id,
        Cloud.id == instance_id
    )).first()
    hostname = cloud_with_user.Cloud.hostname
    
    app = db.session.query(CloudApp).filter(id == app_id)
    # phpapp = CloudApp("PHP", "chialab/php", "8080", True, "blue", 1)
    
    if cloud_with_user is not None:
        cloud_secret = cloud_with_user.app_secret_access
        try:
            myvpc = db.session.query(VPC).filter(user_id == current_user.id)
            param = {
                "cloudid": cloud_with_user.Cloud.id,
                "appid" : app_id,
                "secret" : cloud_secret,
                "action" : "deploy",
                "lb_subnet" : myvpc.default_subnet_id,
                "lb_subnet_sub" : myvpc.sub_subnet_id
            }
            result = app_commander(param)
            # newcloud = CloudAppAssigned(cloud_with_user.Cloud.id, app_id )
            if result == True:
                    
                return {
                    "success" : True
                }
            else:
                return {
                    "success" : False
                }
        except Exception as e:
            return {
                "success" : False,
                "message" : "deploy exception, message: {}".format(e)
            }
        
    else:
        return {
            "success" : False,
            "message" : "cloud owner not matched"
        }
    
    
    
    pass


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
            response = delete_ec2(cloud_with_user.Cloud.aws_instance_id, cloud_with_user.Cloud.certificate_arn)
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



@cloud_blueprint.route("/detail/<cloud_id>/<metrictype>/<hour>", methods=["GET"])
@login_required # image provider metrics
def get_metrics(cloud_id, metrictype, hour):
    cwclient = boto3.client(service_name='cloudwatch') 
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(Cloud.id == cloud_id).first()
    if cloud_with_user is not None:
        # x = '{{"view":"timeSeries","stacked":false,"metrics":[["AWS/EC2","{metricName}"]],"width":1041,"height":250,"start":"-PT3H","end":"P0D"}}'.format(metricName="CPUUtilization")
        x = '{{"view":"timeSeries","stacked":false,"metrics":[["AWS/EC2","{metricName}", "InstanceId", "{InstanceId}"]],"width":1041,"height":250,"start":"-PT{hour}H","end":"P0D"}}'.format(metricName=metrictype, hour=hour, InstanceId=cloud_with_user.Cloud.aws_instance_id)
        output = cwclient.get_metric_widget_image(
            MetricWidget=x
        )
        
        return send_file(io.BytesIO(output["MetricWidgetImage"]),mimetype='image/jpeg') 
    else:
        message = Markup("<strong>잘못된 접근입니다.</strong>  ")
        flash(message, 'danger')
    
    return redirect(url_for('home'))
        
    

@cloud_blueprint.route("/<cloud_id>/detail", methods=['GET'])
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
             
            return render_template('cloud/detail.html', cloud=response, screenshot=screenshot, output=output, traffic=outbound_traffic,cloudid=cloud_id)
        else:
            message = Markup("<strong>잘못된 접근입니다.</strong>  ")
            flash(message, 'danger') 
    else:
        message = Markup("<strong>잘못된 접근입니다.</strong>  ")
        flash(message, 'danger')
    
    return redirect(url_for('home'))

@cloud_blueprint.route("/file", methods=["GET", "POST"])
@login_required
def file():
    # upload / create / delete  / view
    # public_html
    
    
    pass

@cloud_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_cloud():
    form = CloudForm(request.form)
    plans = Plan.query.all()
    os_list = Oslist.query.all() 
    keypair_list = db.session.query(Keypair.id, Keypair.name).filter(Keypair.user_id == current_user.id )
    sec_list = db.session.query(SecurityGroup).filter(SecurityGroup.user_id == current_user.id)
    
    credit_sum = db.session.query(Balance.balance).filter_by(user_id=current_user.id).scalar()
    app_name = form["appname"]
    
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
                aws_image = db.session.query(Oslist.aws_image_id, Oslist.os_name).filter(Oslist.id == form.data["os"])[0]
                
                vpc_id = vpc_info[4]
                vpc_default_subnetid = vpc_info[2]
                vpc_default_secid = vpc_info[3]
                keypair_id = form.data["keypair"]

                if check_environment(current_user.id) == True: 
                    # 기존 키 페어 찾아서 클라우드에 반영
                    get_keypair = db.session.query(Keypair.name, Keypair.keytoken).filter(Keypair.id == keypair_id).first()
                    keypairname_formatted = "{}_{}".format( get_keypair.keytoken , get_keypair.name) 

                    # DB에 기록
                    new_cloud = Cloud(form.data["Hostname"], form.data["plan"], current_user.id, form.data["os"], "Queued", "Requesting", "Seoul" , keypair_id , vpc_id, "Requesting", "creating")
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
                        "os" : aws_image.aws_image_id,
                        "subnetid" : vpc_default_subnetid,
                        "keypair" : keypairname_formatted,
                        "security-group-id" : [get_sec_id],
                        "cloudid" : assigned_id,
                        "os_name" :  aws_image.os_name,
                        "hostname" : new_cloud.hostname
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

