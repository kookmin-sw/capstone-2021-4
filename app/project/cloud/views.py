from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project import app
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityRule, NetInterface
import boto3
import os
from .forms import CloudForm, EditCloudForm
import project.cloud.utils as awsutil

import time 
# # CONFIG
cloud_blueprint = Blueprint('cloud', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 

@cloud_blueprint.route('/list', methods=['GET'])
@login_required
def all_clouds():
    # job = q.enqueue(background_task, request.args.get("n"))
    # Check Status, IPAddr, Status
    cloud_lists = db.session.query(Plan, Cloud,Oslist).join(Cloud).filter(Cloud.user_id == current_user.id,Cloud.os == Oslist.id)
    
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

@cloud_blueprint.route('/delete/<instance_id>', methods=['POST'])
@login_required
def delete_cloud():

    return "Deleted Instance"

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
        CidrBlock='172.0.0.0/16', # CIDR : 172.0.0.0 ~ 172.0.255.255 65536 Hosts
    )
    
    return response

def back_ec2_create_net_interface(subnetid):
    response = ec2.create_network_interface(
        Description='string',   
        SubnetId=subnetid,
        TagSpecifications=[
            {
                'ResourceType': 'network-interface' ,
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


def back_ec2_delete_net_interface(interfaceid):
    response = ec2.delete_network_interface(
        # NetworkInterfaceId='eni-e5aa89a3',
        NetworkInterfaceId=interfaceid
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
        CidrBlock='172.0.1.0/20',  
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
                'ResourceType': 'internet-gateway',
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


def back_ec2_int_gateway_attach_vpc(intgatewayid, vpc_id): 
    response = ec2.attach_internet_gateway( 
        InternetGatewayId=intgatewayid,
        VpcId=vpc_id
    )
    return response

def back_ec2_int_gateway_detach_vpc(intgatewayid, vpc_id): 
    response = ec2.detach_internet_gateway( 
        InternetGatewayId=intgatewayid,
        VpcId=vpc_id
    )
    return response



def back_ec2_create_security_group(vpc_id):
    response = ec2.create_security_group(
        Description='string',
        GroupName='string',
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'security-group',
                'Tags': [
                    {
                        'Key': 'string',
                        'Value': 'string'
                    },
                ]
            },
        ], 
    )
    return response

def find_route_table(vpc_id,Index=0):
    response = ec2.describe_route_tables(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc_id,
                ]
            },
        ],
        MaxResults=100
    )
    route_table_id = response["RouteTables"][Index]["RouteTableId"] 
    return route_table_id

def route_table_init( inter_gw_id, route_table_id): 
    response = ec2.create_route(
        DestinationCidrBlock='0.0.0.0/0', 
        GatewayId=inter_gw_id,     
        RouteTableId=route_table_id,  
    ) 
    return response

def check_environment(userid):
    result = db.session.query(VPC.vpc_id).filter(VPC.user_id == userid).scalar() # VPC check  
    if result == None:
        return False # 환경구축이 필요함
    else:
        return True

def set_default_security_group(sec_group_id):
    response = ec2.authorize_security_group_ingress(
        GroupId=sec_group_id,
        IpPermissions=[
            {
                'FromPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'SomeCloud Default Security rule',
                    },
                ],
                'ToPort': 22,
            },
        ],
    ) 
    print(response)
    return response 


def create_environment(userid): # 사용자마다 한번씩만 해주는..
    try:
        print("[Console] Create_env Started")
        vpc_result = back_ec2_create_vpc() 
        print("[Console] VPC Create")
        vpc_id = vpc_result["Vpc"]["VpcId"]
        
        print("[Console] Subnet Create")
        subnet_res = back_ec2_create_subnet(vpc_id)
        subnet_id = subnet_res["Subnet"]["SubnetId"]
        subnet_cidr = subnet_res["Subnet"]["CidrBlock"] 
        print("[Console] Internet Gateway Create")
        int_gateway = back_ec2_create_int_gateway(vpc_id)
        int_gw_id = int_gateway["InternetGateway"]["InternetGatewayId"]
        print("[Console] VPC-Internet GW Attach")
        back_ec2_int_gateway_attach_vpc(int_gw_id, vpc_id)
        
        route_table_id = find_route_table(vpc_id)
        print("[Console] RouteTable Init - {}".format(route_table_id))
        router_init = route_table_init(int_gw_id, route_table_id)
        print("[Console] SecurityGroup Create")
        security_group = back_ec2_create_security_group(vpc_id)   
        security_group_id = security_group["GroupId"] 
        print("[Console] SecurityGroup {} created".format(security_group_id))
        set_default_security_group(security_group_id) # add port 22
        print("[Console] SecurityGroup Default Port 22 added")

        print("[Console] DB Record create")
        # Create record structure
        new_subnet = Subnet(subnet_id, subnet_cidr)
        new_vpc = VPC(userid, vpc_id, int_gw_id, subnet_id ,security_group_id )
        new_security_rule = SecurityRule(security_group_id, userid)
        print("[Console] DB Commit")
        # Apply to DB 
        db.session.add(new_subnet)
        db.session.add(new_vpc)
        
        db.session.add(new_security_rule)

        db.session.commit()  
        print("[Console] created user environment")
    except:
        print("[Console] Error..")
        # delete_environment(current_user.id)
        # print("[Console] VPC deleting")
        # response =ec2.delete_vpc(
        #     VpcId=vpc_id
        # )
        print(response)
        print("DB rollback process..")
        db.session.rollback()
    

def delete_environment(userid):
    # delete vpc table on vpc id
     
    pass
 


def back_ec2_create_ec2( param):
    # parameter = {
    #                     "plan" : param_plan,
    #                     "iops" : param_iops,
    #                     "ssd" : param_ssd,
    #                     "subnetid" : vpc_default_subnetid,
    #                     "keypair" : keypairname_formatted,
    #                     "security-group-id" : [get_sec_id]
    #                 }
    print("PARAM")
    print(param)
    instance = ec2.run_instances(
    BlockDeviceMappings=[ # 이게 기본 부트 볼륨으로 지정이 안됨.. /dev/sda1 같은거로 바꾸고, VolumeType, IOPS 세팅 피룡함
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "DeleteOnTermination": True, 
                "VolumeSize": param["ssd"], 
                "VolumeType": "gp3",
                "Iops" : param["iops"],
                "Throughput" : 125,
                "DeleteOnTermination": True,
            }
        } 
    ],
    ImageId='ami-b2f152dc',
    InstanceType="t3.micro", 
    KeyName=param["keypair"],
    MaxCount=1,
    MinCount=1,
    Monitoring={ # 이건 대체 머하는옵션
        'Enabled': True 
    }, 
    NetworkInterfaces=[
    { 
        "AssociatePublicIpAddress": True,
        "DeviceIndex": 0,
        'SubnetId': param["subnetid"],
        'Groups' : param["security-group-id"],
        "DeleteOnTermination": True,
    }, 
    ]  
    # UserData='string', # StackScript 같은거..  
    )
    print(instance) 
    return instance 

 
@cloud_blueprint.route("/detail/<cloud_id>", methods=['GET'])
@login_required
def detail(cloud_id):
    cloud_with_user = db.session.query(Cloud, User).join(User).filter(Cloud.id == cloud_id).first()
    if cloud_with_user is not None:
        if current_user.is_authenticated and cloud_with_user.Cloud.user_id == current_user.id:
            # show cloud detail
            # print(cloud_with_user.Cloud.aws_instance_id )
            idtest = cloud_with_user.Cloud.aws_instance_id 
            response = ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'instance-id',
                        'Values': [
                            idtest,
                        ]
                    },
                ],   
            )
             
            print(response)
            return render_template('cloud_detail.html', cloud_detail=cloud_with_user)
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
                    
                    parameter = {
                        "plan" : param_plan,
                        "iops" : param_iops,
                        "ssd" : param_ssd,
                        "subnetid" : vpc_default_subnetid,
                        "keypair" : keypairname_formatted,
                        "security-group-id" : [get_sec_id]
                    }
                    
                    job = q.enqueue(back_ec2_create_ec2, parameter)
                    print("Task ({}) added to queue at {}".format(job.id, job.enqueued_at))
                    # result = back_ec2_create_ec2( )
                    # instance_id = result["Instances"][0]["InstanceId"]
                    new_cloud = Cloud(form.data["Hostname"], form.data["plan"], current_user.id, form.data["os"], "Queued", "Requesting", "Seoul" , keypair_id , vpc_id, "Requesting")
                    db.session.add(new_cloud) 
                    db.session.commit()
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

