import os
from project import app
import boto3
from project import db
from project import q
from project import r
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityGroup, NetInterface, SecurityRule, CloudApp,CloudAppCommand
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

def insert_app(app_name, soruce, port, rollback ):
    capp = CloudApp(app_name, source, port, rollback)
    db.session.add(capp)
    db.session.commit()

def insert_app_command(action, script, app_id, sequence_num):
    db.session.add(CloudAppCommand(action, script,app_id, sequence_num))
    db.session.commit()

def create_lb_target_group():
    elbclient = boto3.client('elbv2')
    response = elbclient.create_target_group(
        Name='string',
        Protocol='HTTP'|'HTTPS'|'TCP'|'TLS'|'UDP'|'TCP_UDP'|'GENEVE',
        ProtocolVersion='string',
        Port=123,
        VpcId='string',
        HealthCheckProtocol='HTTP'|'HTTPS'|'TCP'|'TLS'|'UDP'|'TCP_UDP'|'GENEVE',
        HealthCheckPort='string',
        HealthCheckEnabled=True|False,
        HealthCheckPath='string',
        HealthCheckIntervalSeconds=123,
        HealthCheckTimeoutSeconds=123,
        HealthyThresholdCount=123,
        UnhealthyThresholdCount=123,
        Matcher={
            'HttpCode': 'string',
            'GrpcCode': 'string'
        },
        TargetType='instance'|'ip'|'lambda',
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            },
        ]
    )
    pass


def create_loadbalancer_env(param):
    
    elbclient = boto3.client('elbv2')
    #param - loadbalancer - subnet id
    response = elbclient.create_load_balancer(
        Name='string',
        Subnets=[
            'string',
        ],
        SubnetMappings=[
            {
                'SubnetId': 'string',
                'AllocationId': 'string',
                'PrivateIPv4Address': 'string',
                'IPv6Address': 'string'
            },
        ],
        SecurityGroups=[
            'string',
        ],
        Scheme='internet-facing'|'internal',
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            },
        ],
        Type='application'|'network'|'gateway',
        IpAddressType='ipv4'|'dualstack',
        CustomerOwnedIpv4Pool='string'
    )

    
    response = client.create_rule(
        ListenerArn='string',
        Conditions=[
            {
                'Field': 'string',
                'Values': [
                    'string',
                ],
                'HostHeaderConfig': {
                    'Values': [
                        'string',
                    ]
                },
                'PathPatternConfig': {
                    'Values': [
                        'string',
                    ]
                },
                'HttpHeaderConfig': {
                    'HttpHeaderName': 'string',
                    'Values': [
                        'string',
                    ]
                },
                'QueryStringConfig': {
                    'Values': [
                        {
                            'Key': 'string',
                            'Value': 'string'
                        },
                    ]
                },
                'HttpRequestMethodConfig': {
                    'Values': [
                        'string',
                    ]
                },
                'SourceIpConfig': {
                    'Values': [
                        'string',
                    ]
                }
            },
        ],
        Priority=123,
        Actions=[
            {
                'Type': 'forward'|'authenticate-oidc'|'authenticate-cognito'|'redirect'|'fixed-response',
                'TargetGroupArn': 'string',
                'AuthenticateOidcConfig': {
                    'Issuer': 'string',
                    'AuthorizationEndpoint': 'string',
                    'TokenEndpoint': 'string',
                    'UserInfoEndpoint': 'string',
                    'ClientId': 'string',
                    'ClientSecret': 'string',
                    'SessionCookieName': 'string',
                    'Scope': 'string',
                    'SessionTimeout': 123,
                    'AuthenticationRequestExtraParams': {
                        'string': 'string'
                    },
                    'OnUnauthenticatedRequest': 'deny'|'allow'|'authenticate',
                    'UseExistingClientSecret': True|False
                },
                'AuthenticateCognitoConfig': {
                    'UserPoolArn': 'string',
                    'UserPoolClientId': 'string',
                    'UserPoolDomain': 'string',
                    'SessionCookieName': 'string',
                    'Scope': 'string',
                    'SessionTimeout': 123,
                    'AuthenticationRequestExtraParams': {
                        'string': 'string'
                    },
                    'OnUnauthenticatedRequest': 'deny'|'allow'|'authenticate'
                },
                'Order': 123,
                'RedirectConfig': {
                    'Protocol': 'string',
                    'Port': 'string',
                    'Host': 'string',
                    'Path': 'string',
                    'Query': 'string',
                    'StatusCode': 'HTTP_301'|'HTTP_302'
                },
                'FixedResponseConfig': {
                    'MessageBody': 'string',
                    'StatusCode': 'string',
                    'ContentType': 'string'
                },
                'ForwardConfig': {
                    'TargetGroups': [
                        {
                            'TargetGroupArn': 'string',
                            'Weight': 123
                        },
                    ],
                    'TargetGroupStickinessConfig': {
                        'Enabled': True|False,
                        'DurationSeconds': 123
                    }
                }
            },
        ],
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            },
        ]
    )
    return response
    pass


def change_target_group_port():
    pass


def app_commander(param):
    # app command 에 있는거 순서대로 입력해야함
    cloud = Cloud.query.filter_by(id=param["cloudid"]).first()
    command = CloudAppCommand.query.filter_by(app_id = param["appid"], action=param["action"]).order_by(CloudAppCommand.sequence_num.asc())
    ip_addr = cloud.ip_addr
    aws_instance = cloud.aws_instance_id
    vpc_id = cloud.vpc_id
    
    try:
        for item in command:
            if item.command_type == "script":
                response = requests.get("http://{}:61331/run/{}?shell={}".format(ip_addr,secret,item.script))
            
                if response.status_code == 200:
                    print(response.content.decode("utf-8")) 
                else:
                    print("Error")
            elif item.command_type == "api":
                eval(item.script)
           
        
        return True
    except Exception as e:
        print(e)
        return False

def deploy_app(instance_id, app_name):
    pass

def update_app(instance_id, app_name):
    pass

def stop_app(instance_id, app_name):
    pass

def start_app(instance_id, app_name):
    pass

def rollback_app(instance_id, app_name):
    #ignore nginx
    
    pass 

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

def add_default_security_rule(sec_group_id):
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[default_sec_rule],
        )
        
        ec2.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[somecloud_app_rule],
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
        security_group_id = security_group["GroupId"] 
        print("[Console] SecurityGroup {} created".format(security_group_id))
        add_default_security_rule(security_group_id) # add port 22
        
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
        new_security_group = SecurityGroup("DefaultRule" , security_group_id, userid, None, vpc_id)
        db.session.add(new_security_group)
        db.session.flush()
        db.session.refresh(new_security_group)
        sec_group_id = new_security_group.id 
        print("[Console] Sec rule Create")
        new_security_rule = SecurityRule("tcp", "22","22", "0.0.0.0/0", "ssh", sec_group_id)
        db.session.add(new_security_rule)
        
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
    
    use_userdata = ""
    if param["os_name"] == "ubuntu20.04":
        use_userdata = ubuntu_docker_install
    elif param["os_name"] == "amazonLinux":
        use_userdata = amz_docker_install
    
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
 
 