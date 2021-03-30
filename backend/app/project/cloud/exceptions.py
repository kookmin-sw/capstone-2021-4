class EC2Exeption(Exception):
    pass

class VPCException(Exception):
    
    def rollback(scope):
        pass
    
    pass

# Create
class FailToCreateVPCExeption(VPCException):
    pass

class FailToCreateSubnetException(VPCException):
    
    pass

class FailToCreateIntGatewayException(VPCException):
    pass

class FailToAttachIntGatewayVPC(VPCException):
    pass

class FailToFindRouteTable(VPCException):
    pass 

class FailToInitRouteTable(VPCException):
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

class FailToDeleteRouteTable(EC2Exeption):
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

