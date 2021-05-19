import os
from project import app
import boto3
from project import db
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityGroup, NetInterface, SecurityRule,CloudAppCommand
from project.cloud.exceptions import *

ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 

import time
import datetime
import secrets
import requests


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


somecloud_app_rule = {
    'FromPort': 61331,
    'IpProtocol': 'tcp',
    'IpRanges': [
        {
            'CidrIp': '152.67.199.23/32',
            'Description': 'SomeCloud App Security rule',
        },
    ],
    'ToPort': 61331,
}

web_sec_rule_blue = {
    'FromPort': 8080,
    'IpProtocol': 'tcp',
    'IpRanges': [
        {
            'CidrIp': '0.0.0.0/0',
            'Description': 'SomeCloud Default Security rule 8080 ',
        },
    ],
    'ToPort': 8080,
}
web_sec_rule_green = {
    'FromPort': 8081,
    'IpProtocol': 'tcp',
    'IpRanges': [
        {
            'CidrIp': '0.0.0.0/0',
            'Description': 'SomeCloud Default Security rule 8081',
        },
    ],
    'ToPort': 8081,
}



# for lb

web_sec_rule = {
    'FromPort': 80,
    'IpProtocol': 'tcp',
    'IpRanges': [
        {
            'CidrIp': '0.0.0.0/0',
            'Description': 'SomeCloud Default Security rule 80port',
        },
    ],
    'ToPort': 80,
}
web_sec_rule_https = {
    'FromPort': 443,
    'IpProtocol': 'tcp',
    'IpRanges': [
        {
            'CidrIp': '0.0.0.0/0',
            'Description': 'SomeCloud Default Security rule 443 ',
        },
    ],
    'ToPort': 443,
}




def insert_app(app_name, soruce, port, rollback ):
    capp = CloudApp(app_name, source, port, rollback)
    db.session.add(capp)
    db.session.commit()

def insert_app_command(action, script, app_id, sequence_num):
    db.session.add(CloudAppCommand(action, script,app_id, sequence_num))
    db.session.commit()

def create_lb_target_group():
     
    pass


def create_loadbalancer_env(param):
    
    return response
    

def change_target_group_port():
    pass



def app_commander(param):
    # app command 에 있는거 순서대로 입력해야함
    set_port = {
        "blue": 8080,
        "green": 8081
    }
    cloud = Cloud.query.filter_by(id=param["cloudid"]).first()
    command = CloudAppCommand.query.filter_by(app_id = param["appid"], action=param["action"]).order_by(CloudAppCommand.sequence_num.asc())
    ip_addr = cloud.ip_addr
    aws_instance = cloud.aws_instance_id
    vpc_id = cloud.vpc_id
    secret = cloud.app_secret_access
    
    register_target = param["register_target"]
    deregister_target = param["deregister_target"]
    
    client = boto3.client('elbv2')
    if param["action"] == "rollback":
        try:
            
            reg_target = client.register_targets( 
                TargetGroupArn= cloud.targetgroup_arn, # 위에서 만든 target group arn
                Targets=[
                    {
                        'Id': aws_instance, #AWS Instance ID
                        'Port': set_port[register_target], 
                    },
                ]
            )
            print(reg_target)
            
            dreg_target = client.deregister_targets(
                TargetGroupArn=cloud.targetgroup_arn,
                Targets=[
                    {
                        'Id': aws_instance,
                        'Port': set_port[deregister_target]
                    },
                ]
            )
            
            print(dreg_target)
            # 바로 로드벨런서 register -> deregister 순으로 처리
            return {
                "success" : True,
                "message" : "Rollback process completed"
            }
            pass
        
        except Exception as e:
            return e
    elif param["action"] == "update":
        try:

            # 스크립트 수행 후 register -> deregister 순으로 처리
            # 스크립트 -> docker build  ... docker rm -f register_target_port -> docker run -itd register_target:80 register_target_name
            for item in command:
                
                if item.command_type == "script":
                    
                    script_formatted = item.script.format(app_register=register_target, app_port = set_port[register_target] )
                    print(script_formatted)
                    req_url = "http://{}:61331/run?secret={}&shell={}".format(ip_addr,secret,script_formatted)
                    response = requests.get(req_url)
                    print("formatURL: {} ".format(req_url))
                
                    if response.status_code == 200:
                        print(response.content.decode("utf-8")) 
                    else:
                        print("Error")
                        print(response.content)
                elif item.command_type == "api":
                    eval(item.script)
            print("End commend process")
            reg_target = client.register_targets( 
                TargetGroupArn= cloud.targetgroup_arn, # 위에서 만든 target group arn
                Targets=[
                    {
                        'Id': aws_instance, #AWS Instance ID
                        'Port': set_port[register_target], 
                    },
                ]
            )
            print(reg_target)
            
            dreg_target = client.deregister_targets(
                TargetGroupArn=cloud.targetgroup_arn,
                Targets=[
                    {
                        'Id': aws_instance,
                        'Port': set_port[deregister_target]
                    },
                ]
            )
            
            
            return True
        except Exception as e:
            print(e)



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

 

def back_ec2_create_vpc(email=''):
    try: 
        response = ec2.create_vpc(
            CidrBlock='172.0.0.0/16', # CIDR : 172.0.0.0 ~ 172.0.255.255 65536 Hosts
            TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': email 
                    },
                ]
            },
        ]
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

    

def back_ec2_create_subnet(vpcid,zone,cidrblock):
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
            AvailabilityZone=zone, 
            CidrBlock=cidrblock,
            VpcId=vpcid
        ) 
        return response
    except:
        raise FailToCreateSubnetException

# def back_ec2_create_appsubnet(vpcid):
#     back_ec2_create_subnet(vpcid, '172.0.0.128/26', 'PublicSubnet1ID','ap-northeast-2a')
#     back_ec2_create_subnet(vpcid, '172.0.0.192/26', 'PublicSubnet2ID', 'ap-northeast-2b')
    
    
    
def back_ec2_delete_subnet(subnetid):
    try: 
        response = ec2.delete_subnet(
            SubnetId=subnetid,
        )
        print(response)
        return response
    except Exception as e:
        print(e)
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
    except Exception as e:
        print ("INTGW")
        print(intgatewayid)
        print(e)
        return response
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


def back_ec2_create_security_group(vpc_id, group_name='DefaultRule'):
    try:
        response = ec2.create_security_group(
            Description='string',
            GroupName=group_name,
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
        print(response)
        return response
    except Exception as e:
        print(e)
        raise FailToCreateSecurityGroup
    

def back_delete_route_table(route_table_id):
    try:
        response = ec2.delete_route_table(
            RouteTableId=route_table_id
        )
        print(response)
        return response 
    except Exception as e: 
        print(e)
        raise FailToDeleteRouteTable
    

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
        
def add_lb_secruity_rule(sec_group_id):
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[web_sec_rule],
        )
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[web_sec_rule_https],
        )
        
    except Exception as e:
        print(e)
        raise FailToCreateSecurityRule
    pass
    
def add_default_security_rule(sec_group_id):
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[default_sec_rule],  #ssh
        )
        
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[somecloud_app_rule],
        )
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[web_sec_rule_blue],
        )
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[web_sec_rule_green],
        )
        
        
        return True 
    except:
        raise FailToCreateSecurityRule

def create_environment(userid, email): # 사용자마다 한번씩만 해주는..
    try:
        
        print("[Console] Create_env Started email: {}".format(email))
        vpc_result = back_ec2_create_vpc(email) 
        vpc_id = vpc_result["Vpc"]["VpcId"]
        print("[Console] VPC Created {}".format(vpc_id))
        print("[Console] Subnet Create")
        subnet_res = back_ec2_create_subnet(vpc_id, 'ap-northeast-2a','172.0.0.0/26' )
        subnet_id = subnet_res["Subnet"]["SubnetId"]
        subnet_cidr = subnet_res["Subnet"]["CidrBlock"] 
        
        #other zone create zone subnet
        sub_subnet_res = back_ec2_create_subnet(vpc_id, 'ap-northeast-2b', '172.0.0.64/26')
        sub_subnet_id = sub_subnet_res["Subnet"]["SubnetId"]
        
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
        print("[Console] SecurityGroup Create(LB)")
        security_group_for_lb = back_ec2_create_security_group(vpc_id, "DefaultRuleLb")   
        security_group_id = security_group["GroupId"] 
        print("[Console] SecurityGroup {} created".format(security_group_id))
        print("[Console] SecurityGroup LB {} created".format(security_group_for_lb["GroupId"]))
        add_default_security_rule(security_group_id) # add port 22
        add_lb_secruity_rule(security_group_for_lb["GroupId"])
        print("[Console] SecurityGroup Default Port 22 added")
        print("[Console] DB Record create")
        # Create record structure
        print("[Console] VPC record create")
        new_vpc = VPC(userid, vpc_id, int_gw_id, subnet_id ,security_group_id, sub_subnet_id )
        db.session.add(new_vpc)
        db.session.flush()  
        db.session.refresh(new_vpc)
        vpc_id = new_vpc.id
        print("[Console] Subnet record create(Only primary)")
        new_subnet = Subnet(subnet_id, subnet_cidr,vpc_id) 
        db.session.add(new_subnet)
        print("[Console] Security record create")
        new_security_group = SecurityGroup("DefaultRule" , security_group_id, userid, None, vpc_id )
        new_security_group.lb_sec_group_id = security_group_for_lb["GroupId"]
        db.session.add(new_security_group)
        db.session.flush()
        db.session.refresh(new_security_group)
        sec_group_id = new_security_group.id 
        print("[Console] Sec rule Create")
        db.session.add(SecurityRule("tcp", "22","22", "0.0.0.0/0", "ssh", sec_group_id))
        db.session.add(SecurityRule("tcp", "8080","8080", "0.0.0.0/0", "for ", sec_group_id))
        db.session.add(SecurityRule("tcp", "8081","8081", "0.0.0.0/0", "for lb", sec_group_id))
        
    except FailToCreateSubnetException:
        print("[Console] Fail to create Subnet -> Deleting VPC")
        back_delete_vpc(vpc_id)
    except FailToCreateIntGatewayException:
        print("[Console] Fail to create intgateway -> Deleting Int GW, VPC")
        print(back_ec2_delete_subnet(subnet_id))
        back_delete_vpc(vpc_id)
    except FailToAttachIntGatewayVPC:
        print("[Console] Fail to attach gateway -> Deleting Int GW, VPC")
        back_ec2_delete_subnet(subnet_id)
        print(back_ec2_delete_int_gateway(int_gw_id))
        back_delete_vpc(vpc_id)
    except (FailToFindRouteTable, FailToGetRouteTableID):
        print("[Console] Fail to create route table -> Deleting Int GW, VPC, Detach Int GW")
        print(back_ec2_delete_subnet(subnet_id))
        print(back_ec2_int_gateway_detach_vpc(int_gw_id, vpc_id))
        print(back_ec2_delete_int_gateway(int_gw_id))
        print(back_delete_vpc(vpc_id))
    except FailToInitRouteTable:
        print(back_ec2_int_gateway_detach_vpc(int_gw_id, vpc_id)) 
        print(back_ec2_delete_subnet(subnet_id))
        print(back_ec2_delete_int_gateway(int_gw_id))
        print(back_delete_vpc(vpc_id))
    except FailToCreateSecurityGroup:
        print("[Console] Fail to create sec group -> Deleting Int GW, VPC, RouteTable, Detach Int GW")
        back_ec2_delete_subnet(subnet_id) 
        back_ec2_int_gateway_detach_vpc(int_gw_id, vpc_id)
        back_ec2_delete_int_gateway(int_gw_id)
        back_delete_vpc(vpc_id) 
    except FailToCreateSecurityRule:
        print("[Console] Fail to create sec group rule -> Deleting Int GW, VPC, RouteTable, SecGroup, Detach Int GW")
        back_ec2_delete_subnet(subnet_id)
        back_ec2_delete_security_group(sec_group_id) 
        back_ec2_delete_security_group(security_group_for_lb["GroupId"]) 
        back_ec2_int_gateway_detach_vpc(int_gw_id, vpc_id)
        detach_internet_gateway(int_gw_id, vpc_id)
        back_ec2_delete_int_gateway(int_gw_id)
        back_delete_vpc(vpc_id) 
    except Exception as e:
        print("[Console] 다른 예외 발생 error message start ")
        print(e)
        print("[Console] Error msg end")
        
        db.session.rollback()
        back_ec2_delete_subnet(subnet_id)
        back_ec2_delete_security_group(sec_group_id) 
        back_ec2_int_gateway_detach_vpc(int_gw_id, vpc_id)
        detach_internet_gateway(int_gw_id, vpc_id)
        back_ec2_delete_int_gateway(int_gw_id)
        back_delete_vpc(vpc_id)
    else:
        print("[Console] Transaction 처리 성공")
        db.session.commit()
        print("[Console] DB Commit")
      
        print("[Console] created user environment")
        
    

def back_delete_vpc(vpc_id):
    # delete vpc table on vpc id
    try:
        response =ec2.delete_vpc(
            VpcId=vpc_id
        )
        print("Delete status")
        print(response)
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
    cloud_vpc = VPC.query.filter_by(id=cloud.vpc_id).first()
    net_interface_id = response["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["NetworkInterfaceId"]
    # print(net_interface_id)
    
    subnet_id = response["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["SubnetId"]
    subnet = Subnet.query.filter_by(subnet_id=subnet_id).first()
    subnet_id = subnet.id  
    cloud_id = cloud.id 
    db.session.commit()
    selected_os = Oslist.query.filter_by(id = cloud.os).first()
    print("OS : {}".format(selected_os.os_name))
    print("HostedZoneID {}".format(os.getenv("HOSTED_ZONE_ID")))
    hosted_zone_id = os.getenv("HOSTED_ZONE_ID")
    if selected_os.os_name == "flask":
        print("LB Deployment started")
        client = boto3.client('elbv2')
        tg = client.create_target_group(
            Name="tg-{}".format(secrets.token_hex(nbytes=5)),
            Port=8080,
            Protocol='HTTP',
            VpcId=cloud_vpc.vpc_id,
        )
        cloud.targetgroup_arn = tg["TargetGroups"][0]["TargetGroupArn"]
        db.session.commit()
        print("wait for 10 sec for instance state running")
        time.sleep(10)
        rp = client.register_targets( 
            TargetGroupArn= tg["TargetGroups"][0]["TargetGroupArn"], # 위에서 만든 target group arn
            Targets=[
                {
                    'Id': instance_id, #AWS Instance ID
                    'Port': 8080, 
                },
            ]
        )
        sel_secgroup = db.session.query(SecurityGroup).filter(SecurityGroup.id == cloud.sec_group_id).first()
        lb1 = client.create_load_balancer(
            Name="lb1-{}".format(secrets.token_hex(nbytes=5)),
            Subnets=[
                cloud_vpc.default_subnet_id,
                cloud_vpc.sub_subnet_id
            ], 
            SecurityGroups=[
                sel_secgroup.lb_sec_group_id,
            ],
            Scheme='internet-facing',
            Tags=[
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ],
            Type='application' ,
            IpAddressType='ipv4',
        )
        
        lb_hostname = lb1["LoadBalancers"][0]["DNSName"]
        client = boto3.client('route53')
        print(cloud.hostname + ".some-cloud.net DNS Record create process")
        response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id, # 이건 Static 한 값이 되겠다.. 고객별로 도메인을 등록하는것까지 할 수 있겠지만 ,, cost 가 늘어난다... ㅜ ㅜ 
            ChangeBatch={
                'Comment': '12d12d12d12',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': cloud.hostname + ".some-cloud.net" ,
                            'Type': 'CNAME',  
                            'TTL': 300,
                            'ResourceRecords': [
                                {
                                    'Value': lb_hostname
                                },
                            ],  
                        }
                    },
                ]
            }
        )
        client = boto3.client('acm')
        response = client.describe_certificate(
            CertificateArn=cloud.certificate_arn
        )
        certvalidation_domain = response["Certificate"]["DomainValidationOptions"][0]["ResourceRecord"]["Name"]
        certvalidation_value =  response["Certificate"]["DomainValidationOptions"][0]["ResourceRecord"]["Value"]
        client = boto3.client('route53')
        response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id, # 이건 Static 한 값이 되겠다.. 고객별로 도메인을 등록하는것까지 할 수 있겠지만 ,, cost 가 늘어난다... ㅜ ㅜ 
            ChangeBatch={
                'Comment': '12d12d12d12',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': certvalidation_domain,
                            'Type': 'CNAME',  
                            'TTL' : 300,
                            'ResourceRecords': [
                                {
                                    'Value': certvalidation_value
                                },
                            ],  
                        }
                    },
                ]
            }
        )
        time.sleep(30)
        client = boto3.client('elbv2')
        response = client.create_listener(
            LoadBalancerArn=lb1["LoadBalancers"][0]["LoadBalancerArn"],
            Protocol='HTTP',
            Port=80,  
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': tg["TargetGroups"][0]["TargetGroupArn"],
                },
            ], 
            Tags=[
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ]
        )
        response = client.create_listener(
            LoadBalancerArn=lb1["LoadBalancers"][0]["LoadBalancerArn"],
            Protocol='HTTPS',
            Port=443,  
             Certificates=[
                {
                    'CertificateArn': cloud.certificate_arn, 
                },
            ],
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': tg["TargetGroups"][0]["TargetGroupArn"],
                },
            ], 
            Tags=[
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ]
        )
        

        
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


 

def delete_ec2(instance_id, cert_arn):
    client = boto3.client('acm')
    # -> flask app 이면 로드벨런서 삭제 후 cert 삭제..!
    # 그게 아니면 cert삭제
    # response = client.delete_certificate(
    #     CertificateArn=cert_arn
    # )
    # dns record delete
    # 
    
    response = ec2.terminate_instances(
        InstanceIds=[
            instance_id,
        ] 
    )
    return response



def back_ec2_create_ec2( param):
    client = boto3.client('acm')
    
    response = client.request_certificate(
        DomainName=param["hostname"] + ".some-cloud.net", # arn:aws:acm:ap-northeast-2:453409655393:certificate/bc65ddcb-9963-4d29-bd9f-f98f9569fcdd
        ValidationMethod='DNS',   
        Options={
            'CertificateTransparencyLoggingPreference':  'DISABLED'
        },  
    )
    cert_arn = response["CertificateArn"]

    secret_key=secrets.token_hex()
    print("secKey: {}".format(secret_key))
    amz_docker_install = """
    
    #!/bin/bash
    mkdir -p /home/ec2-user/.manager 
    mkdir -p /home/ec2-user/public_html 
    chown -R ec2-user:ec2-user /home/ec2-user/.manager
    sudo yum install docker git python3.7 -y 
    git clone https://github.com/kookmin-sw/capstone-2021-4 -b backend /home/ec2-user/.manager
    cd capstone-2021-4/backend/receiver/ 
    chmod +x run.sh 
    cd ~/ 
    sudo usermod -a -G docker ec2-user 
    sudo systemctl start docker && sudo systemctl enable docker 
    #set secret key
    echo 'export secret={}' >> /home/ec2-user/.bashrc
    # permission
    chown -R ec2-user:ec2-user /home/ec2-user/.manager
    
    
    #start up like rc.local
    """.format(secret_key)
    ubuntu_docker_install = """
    #!/bin/bash \n
    wget https://get.docker.com\n
    chmod 777 index.html
    ./index.html\n
    sudo usermod -a -G docker ubuntu \n
    sudo systemctl enable docker \n
    """
    flask_install = """
    #!/bin/bash
    sudo service supervisord stop
    cd /home/ec2-user/.manager/capstone-2021-4/backend
    git reset --hard
    git clean -d -f -f
    git pull
    cp -rf /home/ec2-user/.manager/capstone-2021-4/backend/receiver/flask.ini /etc/supervisord.d/
    echo 'environment=secret={}' >> /etc/supervisord.d/flask.ini
    sudo service supervisord start
    """.format(secret_key)
    
    use_userdata = ""
    if param["os_name"] == "ubuntu20.04":
        use_userdata = ubuntu_docker_install
    elif param["os_name"] == "amazonLinux":
        use_userdata = amz_docker_install
        # load balancer create
    elif param["os_name"] == "flask":
        print("secret install : {} ".format(flask_install) )
        use_userdata = flask_install
        
        

    
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
    UserData=use_userdata,
    
    NetworkInterfaces=[
    { 
        "AssociatePublicIpAddress": True, # no need to change subnet attribute 'ipv4 auto assign'
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
    cloud.app_secret_access = secret_key
    cloud.certificate_arn = cert_arn
    secgroup = SecurityGroup.query.filter_by(sec_group_id=param["security-group-id"][0]).first()
    secgroup.associated_to = cloud_id
    
  

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
 
 