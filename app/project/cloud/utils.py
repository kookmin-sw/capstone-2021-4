import os
from project import app
import boto3
from project import db
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityRule, NetInterface
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 
import time

def reboot_instances():
    
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
        print("DB rollback process..")
        db.session.rollback()
    

def delete_environment(userid):
    # delete vpc table on vpc id
     
    pass
 
def back_update_ec2_info(instance_id):
    time.sleep(5)
    response = back_ec2_instance_detail(instance_id)
    ip_addr = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    if ip_addr == None:
        q.enqueue(back_update_ec2_info, instance_id) #5 초 뒤에 다시 시도!!
        print("[Console] Ec2 Instance Public IP is not assigned, check EC2 Console. Retry after 5 seconds")
    else:
        cloud = Cloud.query.filter_by(aws_instance_id=instance_id).first()
        cloud.ip_addr = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        db.session.add(cloud)
        db.session.commit()

def delete_ec2(instance_id):
    response = ec2.terminate_instances(
        InstanceIds=[
            instance_id,
        ] 
    )
    return response

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
    cloud_id = param["cloudid"]
    instance_id = instance["Instances"][0]["InstanceId"]
    cloud = Cloud.query.get(cloud_id)
    cloud.aws_instance_id = instance_id
    cloud.status = "Running"
    
    db.session.commit() 
    q.enqueue(back_update_ec2_info, instance_id)
    print(instance)
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
 
 