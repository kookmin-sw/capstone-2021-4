class EC2Exeption(Exception):
    pass

# Create
class FailToCreateVPCExeption(EC2Exeption):
    pass

class FailToCreateSubnetException(EC2Exeption):
    pass

class FailToCreateIntGatewayException(EC2Exeption):
    pass

class FailToAttachIntGatewayVPC(EC2Exeption):
    pass

class FailToFindRouteTable(EC2Exeption):
    pass 

class FailToInitRouteTable(EC2Exeption):
    pass

class FailToCreateSecurityGroup(EC2Exeption):
    pass

class FailToCreateSecurityRule(EC2Exeption):
    pass

class FailToCreateNetInterface(EC2Exeption):
    pass



# Delete

class FailToDeleteNetInterface(EC2Exeption):
    pass

class FailToDeleteSubnet(EC2Exeption):
    pass 

class FailToDeleteIntGateway(EC2Exeption):
    pass

class FailToDeleteVPC(EC2Exeption):
    pass

class FailToDeleteSecurityGroup(EC2Exeption):
    pass


# Detach

class FailToDetachIntGatewayFromVPC(EC2Exeption):
    pass

 
# Others

class FailToCheckEnvironment(Exception):
    pass

class FailToGetScreenShot(Exception):
    pass


class FailToGetRouteTableID(Exception):
    pass

