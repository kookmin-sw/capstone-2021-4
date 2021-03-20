import os
from project import app
import boto3
from project import db
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityGroup, NetInterface, SecurityRule
from project.cloud.exceptions import *

ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 
import time
import datetime

default_sec_rule = {
    'FromPort': 22,
    'IpProtocol': 'tcp',
    'IpRanges': [
        {
            'CidrIp': '0.0.0.0/0',
            'Description': 'SomeCloud Default Security rule',
        },
    ],
    'ToPort': 22,
}


def reboot_instances(instance_id):
    response = ec2.reboot_instances(InstanceIds=[instance_id], DryRun=False)
    return response

def get_console_screenshot(instance_id):
    try:
        response = ec2.get_console_screenshot(
            InstanceId=instance_id,
            WakeUp=True
        ) 
        return response
    except:
        raise FailToGetScreenShot
    

def get_console_output(instance_id):
    response = ec2.get_console_output(
        InstanceId=instance_id
    )
    return response

 

def back_ec2_create_vpc():
    try: 
        response = ec2.create_vpc(
            CidrBlock='172.0.0.0/16', # CIDR : 172.0.0.0 ~ 172.0.255.255 65536 Hosts
        )
        return response
    except:
        raise FailToCreateVPCExeption

def back_ec2_create_net_interface(subnetid):
    try:
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
    except:
        raise FailToCreateNetInterface
    


def back_ec2_delete_net_interface(interfaceid):
    try:
        response = ec2.delete_network_interface(
            # NetworkInterfaceId='eni-e5aa89a3',
            NetworkInterfaceId=interfaceid
        )
        return response 
    
    except:
        raise FailToDeleteNetInterface

    

def back_ec2_create_subnet(vpcid):
    try: 
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
    except:
        raise FailToCreateSubnetException

    
    
def back_ec2_delete_subnet(subnetid):
    try: 
        response = ec2.delete_subnet(
            SubnetId=subnetid,
        )
        return response
    except:
        raise FailToDeleteSubnet


def back_ec2_create_int_gateway():
    try:
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
    except:
        raise FailToCreateIntGatewayException
    
def back_ec2_delete_int_gateway(intgatewayid):
    try:
        response = ec2.delete_internet_gateway( 
            InternetGatewayId=intgatewayid
        )
        return response
    except:
        raise FailToDeleteIntGateway

def back_ec2_int_gateway_attach_vpc(intgatewayid, vpc_id): 
    try:
        response = ec2.attach_internet_gateway( 
            InternetGatewayId=intgatewayid,
            VpcId=vpc_id
        )
        return response
    except:
        raise FailToAttachIntGatewayVPC

    

def back_ec2_int_gateway_detach_vpc(intgatewayid, vpc_id): 
    try:
        response = ec2.detach_internet_gateway( 
            InternetGatewayId=intgatewayid,
            VpcId=vpc_id
        )
        return response
    except:
        raise FailToDetachIntGatewayFromVPC
    

def back_ec2_delete_security_group(sec_group_id):
    try: 
        response = ec2.delete_security_group(
            GroupId=sec_group_id 
        )
        return response
    except:
        raise FailToDeleteSecurityGroup 


def back_ec2_create_security_group(vpc_id):
    try:
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
    except:
        raise FailToCreateSecurityGroup
    

def find_route_table(vpc_id,Index=0):
    try:
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
    except (AttributeError, KeyError):
        raise FailToGetRouteTableID
    except:
        raise FailToFindRouteTable

 
    

def route_table_init( inter_gw_id, route_table_id): 
    try:
        response = ec2.create_route(
            DestinationCidrBlock='0.0.0.0/0', 
            GatewayId=inter_gw_id,     
            RouteTableId=route_table_id,  
        ) 
        return response

    except:
        raise FailToInitRouteTable

    

def check_environment(userid):
    try:
        result = db.session.query(VPC.vpc_id).filter(VPC.user_id == userid).scalar() # VPC check  
        if result == None:
            return False # 환경구축이 필요함
        else:
            return True
    except:
        raise FailToCheckEnvironment

def add_default_security_rule(sec_group_id):
    try:
        response = ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[default_sec_rule],
        ) 
        return response 
    except:
        raise FailToCreateSecurityRule

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
        int_gateway = back_ec2_create_int_gateway()
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
        add_default_security_rule(security_group_id) # add port 22
        
        print("[Console] SecurityGroup Default Port 22 added")
        print("[Console] DB Record create")
        # Create record structure
        new_vpc = VPC(userid, vpc_id, int_gw_id, subnet_id ,security_group_id )
        db.session.add(new_vpc)
        db.session.flush()  
        db.session.refresh(new_vpc)
        vpc_id = new_vpc.id
        new_subnet = Subnet(subnet_id, subnet_cidr,vpc_id) 
        db.session.add(new_subnet)
        new_security_group = SecurityGroup("DefaultRule" , security_group_id, userid, None, vpc_id)
        db.session.add(new_security_group)
        db.session.flush()
        db.session.refresh(new_security_group)
        sec_group_id = new_security_group.id 
        new_security_rule = SecurityRule("tcp", "22","22", "0.0.0.0/0", "ssh", sec_group_id)
        db.session.add(new_security_rule)
        print("[Console] DB Commit")
        # Apply to DB 
        db.session.commit()  
        print("[Console] created user environment")

    except:
        print("[Console] Fail to create Sec rule")

        if subnet_id is not None:
            back_ec2_delete_subnet(subnet_id) 
        
        if security_group_id is not None:
            back_ec2_delete_security_group(security_group_id) 

        if int_gw_id is not None and vpc_id is not None:
            back_ec2_int_gateway_detach_vpc(int_gw_id, vpc_id )
            back_ec2_delete_int_gateway(int_gw_id)
            back_delete_vpc(vpc_id)
         
        print("DB rollback process..")
        db.session.rollback()
    

def back_delete_vpc(vpc_id):
    # delete vpc table on vpc id
    try:
        response =ec2.delete_vpc(
            VpcId=vpc_id
        ) 
        return response
    except:
        raise FailToDeleteVPC 
 
def back_update_ec2_info(instance_id):
    time.sleep(5)
    # try:
    response = back_ec2_instance_detail(instance_id)
    
    # status = response["Reservation"][0]["Instances"][0]["StateReason"][0]["Code"]
    # print("Status:".format(status))
    
    print(response)
    ip_addr = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    print(ip_addr)
    cloud = Cloud.query.filter_by(aws_instance_id=instance_id).first()
    cloud.ip_addr = ip_addr
    
    net_interface_id = response["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["NetworkInterfaceId"]
    # print(net_interface_id)
    
    subnet_id = response["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["SubnetId"]
    subnet = Subnet.query.filter_by(subnet_id=subnet_id).first()
    subnet_id = subnet.id  
    cloud_id = cloud.id 
    db.session.commit()
        
    check = db.session.query(NetInterface).filter(NetInterface.cloud_id == cloud_id).first()

    if check is None:
        attached_at = datetime.datetime.now()
        network = NetInterface(net_interface_id, subnet_id, cloud_id, attached_at)
        db.session.add(network)
        db.session.commit()


        
    # except KeyError:
    #     print("[Console] Ec2 Instance Public IP is not assigned, check EC2 Console. Retry after 5 seconds")
    #     # q.enqueue(back_update_ec2_info, instance_id)
    # if response["Reservation"][0]["Instances"][0]["StateReason"][0]["Code"] == "Client.UserInitiatedShutdown":
    #     print("Terminated. change status to terminated")
    #     now = datetime.datetime.now()
    #     cloud = Cloud.query.filter_by(aws_instance_id=instance_id).first()
    #     cloud.status = "Terminated"
    #     cloud.deleted_at = now.strftime("%Y-%m-%d %H:%M:%S")
    #     db.session.add(cloud)
    #     db.session.commit() 
    #     return
    # except Exception as e:
    #     print("Other Error 다시 시도 ".format(e))
    #     # q.enqueue(back_update_ec2_info, instance_id)
    
    # q.enqueue(back_update_ec2_info, instance_id)
    # db.session.rollback()

def delete_ec2(instance_id):
    response = ec2.terminate_instances(
        InstanceIds=[
            instance_id,
        ] 
    )
    return response

def back_ec2_create_ec2( param): 
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
    ImageId=param["os"],
    InstanceType=param["plan"], 
    KeyName=param["keypair"],
    MaxCount=1,
    MinCount=1,
    Monitoring={  
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
    # UserData='string', # StackScript if exists 
    )
    cloud_id = param["cloudid"]
    instance_id = instance["Instances"][0]["InstanceId"]
    cloud = Cloud.query.filter_by(id=cloud_id).first()
    cloud.aws_instance_id = instance_id
    cloud.status = "Running" 
    secgroup = SecurityGroup.query.filter_by(sec_group_id=param["security-group-id"][0]).first()
    secgroup.associated_to = cloud_id

    db.session.add(cloud)
    db.session.add(secgroup)

    db.session.commit() 
    
    q.enqueue(back_update_ec2_info, instance_id) 
    return instance 

def back_ec2_instance_detail(instance_id):
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [
                    instance_id,
                ]
            },
        ],   
    ) 
    return response
 
 