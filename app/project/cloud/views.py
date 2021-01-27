from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project import app
from project.models import User, Cloud, Plan, Oslist,VPC
import boto3
import os
from .forms import CloudForm, EditCloudForm


# # CONFIG
cloud_blueprint = Blueprint('cloud', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 
# ec2 = boto3.resource('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY"))

@cloud_blueprint.route('/list', methods=['GET'])
@login_required
def all_clouds():
    cloud_lists = Cloud.query.filter_by(user_id = current_user.id)
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
        AvailabilityZone='ap-northwest-2', 
        CidrBlock='100.68.0.0/18',  
        VpcId=vpcid
    )
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


def back_ec2_create_ec2(id, plan, iops ,volumesize ):    
    subnet = ec2.Subnet(id)
    instance = subnet.create_instances(
    BlockDeviceMappings=[
            {
                'DeviceName': 'string',
                'VirtualName': 'string',
                'Ebs': {
                    'DeleteOnTermination': True|False,
                    'Iops': iops, 
                    'VolumeSize': volumesize,
                    'VolumeType': 'gp3' , 
                    'Throughput': 125,
                    'Encrypted': False
                } 
            },
        ],
        ImageId='ami-081c72fa60c8e2d58',
        InstanceType= plan,
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': True|False
        },
        Placement={
            'AvailabilityZone': 'string',
            'Affinity': 'string',
            'GroupName': 'string',
            'PartitionNumber': 123,
            'HostId': 'string',
            'Tenancy': 'default'|'dedicated'|'host',
            'SpreadDomain': 'string',
            'HostResourceGroupArn': 'string'
        },    
        # EbsOptimized=True, 
        InstanceInitiatedShutdownBehavior='terminate',
        NetworkInterfaces=[
            {
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True,
                'Description': 'string',
                'DeviceIndex': 123,
                'Groups': [
                    'string',
                ],
                'Ipv6AddressCount': 123,
                'Ipv6Addresses': [
                    {
                        'Ipv6Address': 'string'
                    },
                ],
                'NetworkInterfaceId': 'string',
                'PrivateIpAddress': 'string',
                'PrivateIpAddresses': [
                    {
                        'Primary': True|False,
                        'PrivateIpAddress': 'string'
                    },
                ],
                'SecondaryPrivateIpAddressCount': 123,
                'SubnetId': 'string',
                'AssociateCarrierIpAddress': True|False,
                'InterfaceType': 'string',
                'NetworkCardIndex': 123
            },
        ], 
        ElasticInferenceAccelerators=[
            {
                'Type': 'string',
                'Count': 123
            },
        ],   
    )
    pass


@cloud_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_cloud():
    form = CloudForm(request.form)
    plans = Plan.query.all()
    os_list = Oslist.query.all() 
    if request.method == 'POST': 
        if form.validate_on_submit():
            vpc_id = ""
            try:
                # 1. AWS EC2 API 호출 - SDK (db 단은 Transaction  수행)
                #  if not have vpc -> create_vpc() / create_internet_gateway()
                check_user_vpc = db.session.query(VPC.id).filter(VPC.user_id == current_user.id).scalar()
                check_plan = db.session.query(Plan.aws_plan, Plan.ssd, Plan.iops ).filter(Plan.id == form.data["plan"])[0]
                aws_plan = check_plan[0]
                aws_ssd = check_plan[1]
                aws_iops = check_plan[2]

                if not check_user_vpc:
                    vpc_result = back_ec2_create_vpc()   
                    new_vpc = VPC(current_user.id, vpc_result["Vpc"]["VpcId"])
                    db.session.add(new_vpc)
                    vpc_id = vpc_result["Vpc"]["VpcId"]
                else:
                    # 기존 VPC가 있을 경우
                    vpc_id = check_user_vpc

                back_ec2_create_ec2(vpc_id, aws_plan, aws_iops,aws_ssd )

                new_cloud = Cloud(form.data["Hostname"], form.data["plan"], current_user.id, form.data["os"], "Queued", "Requesting", "Seoul"  )
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
                if vpc_id:
                    back_ec2_delete_vpc(vpc_id)
                # SDK rollback implement need
                message = Markup(
                    "<strong>내부 API 에러{}".format(mesg))
                flash(message, 'danger')
    else:
        print("GET")
    
    return render_template('add_cloud.html', form=form, planlist = plans, oslist = os_list)

