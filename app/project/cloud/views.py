from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project import app
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair
import boto3
import os
from .forms import CloudForm, EditCloudForm


# # CONFIG
cloud_blueprint = Blueprint('cloud', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 

@cloud_blueprint.route('/list', methods=['GET'])
@login_required
def all_clouds():
    cloud_lists = db.session.query(Cloud).filter(Cloud.user_id == current_user.id)
    return render_template('all_clouds.html', cloud=cloud_lists)

@cloud_blueprint.route('/reboot', methods=['POST'])
@login_required
def reboot_instance():
    try:
        response = ec2.reboot_instances(InstanceIds=['INSTANCE_ID'], DryRun=False)
        print('Success', response)
        return "Success"
    except ClientError as e:
        print('Error', e)

@cloud_blueprint.route('/delete', methods=['POST'])
@login_required
def delete_cloud():
    return "Constructing"

@cloud_blueprint.route("/update", methods=['GET', 'POST'])
@login_required
def update_cloud():
    pass

def back_ec2_delete_vpc(id):
    response = ec2.delete_vpc(
        VpcId=id 
    )
    return response

def back_ec2_create_vpc():
    response = ec2.create_vpc(
        CidrBlock='10.0.0.0/16',
    )
    
    return response

def back_ec2_create_subnet(vpcid):
    response = ec2.create_subnet(
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'string',
                        'Value': 'string'
                    },
                ]
            },
        ],
        AvailabilityZone='ap-northeast-2b', 
        CidrBlock='10.0.1.0/16',  
        VpcId=vpcid
    )
    # 'Subnet': {'AvailabilityZone': 'ap-northeast-2b', 'AvailabilityZoneId': 'apne2-az2', 'AvailableIpAddressCount': 4091, 'CidrBlock': '10.0.0.0/20', 'DefaultForAz': False, 'MapPublicIpOnLaunch': False, 'State': 'available', 'SubnetId': 'subnet-0c6ed9be7c2136f5b', 'VpcId': 'vpc-0c2050c79701c3695', 'OwnerId': '453409655393', 'AssignIpv6AddressOnCreation': False, 'Ipv6CidrBlockAssociationSet': [], 'Tags': [{'Key': 'string', 'Value': 'string'}], 'SubnetArn': 'arn:aws:ec2:ap-northeast-2:453409655393:subnet/subnet-0c6ed9be7c2136f5b'}, 'ResponseMetadata': {'RequestId': '113593d1-9ac0-4a75-b128-9c1b7968e6ef', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '113593d1-9ac0-4a75-b128-9c1b7968e6ef', 'cache-control': 'no-cache, no-store', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'text/xml;charset=UTF-8', 'content-length': '1086', 'date': 'Fri, 29 Jan 2021 11:24:22 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}
    return response
    
def back_ec2_delete_subnet(subnetid):
    response = ec2.delete_subnet(
        SubnetId=subnetid,
    )
    return response

def back_ec2_create_int_gateway(vpcid):
    response = ec2.create_internet_gateway(
        TagSpecifications=[
            {
                'ResourceType': ' internet-gateway',
                'Tags': [
                    {
                        'Key': 'string',
                        'Value': 'string'
                    },
                ]
            },
        ]
    )
    return response 



def back_ec2_delete_int_gateway(intgatewayid):
    pass

def back_ec2_create_ec2( plan, iops ,volumesize , subnet_id, keypair_name):
    instance = ec2.run_instances(
    BlockDeviceMappings=[
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "DeleteOnTermination": True, 
                "VolumeSize": volumesize, 
                "VolumeType": "gp2"
            }
        } 
    ],
    ImageId='ami-b2f152dc',
    InstanceType="t3.micro", 
    KeyName=keypair_name,
    MaxCount=1,
    MinCount=1,
    Monitoring={ # 이건 대체 머하는옵션
        'Enabled': True 
    },
    SecurityGroupIds=[
        'sg-092b8d63',
    ],
    # RamdiskId='string',   
    # UserData='string', # StackScript 같은거..
    # AdditionalInfo='string',
    # ClientToken='string', 
     
     
    )
    return instance 


@cloud_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_cloud():
    form = CloudForm(request.form)
    plans = Plan.query.all()
    os_list = Oslist.query.all() 
    keypair_list = db.session.query(Keypair.id, Keypair.name).filter(Keypair.user_id == current_user.id )
    
    if request.method == 'POST': 
        if form.validate_on_submit(): 
            try:
                vpc_id = ""
                # 1. AWS EC2 API 호출 - SDK (db 단은 Transaction  수행)
                #  if not have vpc -> create_vpc() / create_internet_gateway()
                check_user_vpc = db.session.query(VPC.id).filter(VPC.user_id == current_user.id).scalar()
                check_plan = db.session.query(Plan.aws_plan, Plan.ssd, Plan.iops ).filter(Plan.id == form.data["plan"])[0]
                
                selected_keypair = form.data["keypair"]
                keypair_formatted = "{}_{}".format(current_user.email, db.session.query(Keypair.name).filter(Keypair.id == selected_keypair).scalar())

                aws_plan = check_plan[0]
                aws_ssd = check_plan[1]
                aws_iops = check_plan[2]

                if not check_user_vpc:
                    # 1. Create VPC 
                    vpc_result = back_ec2_create_vpc() 
                    # 2. Create Subnet for VPC
                    vpc_id = vpc_result["Vpc"]["VpcId"]
                    subnet_res = back_ec2_create_subnet(vpc_id)
                    # 3. Getting ID
                    subnet_id = subnet_res["Subnet"]["SubnetId"]
                    subnet_cidr = subnet_res["Subnet"]["CidrBlock"]
                    # 4. Register to DB
                    new_vpc = VPC(current_user.id, vpc_id)
                    
                    db.session.add(new_vpc) 
                    vpc_idx = db.session.query(VPC.id).filter(VPC.vpc_id == vpc_id)
                    db.session.commit()
                    new_subnet = Subnet(subnet_id, subnet_cidr, vpc_idx)
                    db.session.add(new_subnet)
                    db.session.commit()
                else:
                    # 기존 VPC가 있을 경우 기존 vpc사용
                    vpc_id = check_user_vpc 
                # back_ec2_create_ec2( plan, iops ,volumesize , subnet_id, keypair_name)
                subnet_id = db.session.query(Subnet.subnet_id).filter(Subnet.subnet_vpc_id == vpc_id).scalar()
                back_ec2_create_ec2(aws_plan,aws_iops, aws_ssd, subnet_id, keypair_formatted )
                
                new_cloud = Cloud(form.data["Hostname"], form.data["plan"], current_user.id, form.data["os"], "Queued", "Requesting", "Seoul" , selected_keypair )
                db.session.add(new_cloud) 
                db.session.commit()
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
    
    return render_template('add_cloud.html', form=form, planlist = plans, oslist = os_list, keypair = keypair_list)

