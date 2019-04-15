from troposphere import Base64, FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Template, Tags
import troposphere.ec2 as ec2
from magicdict import MagicDict


class MsSql(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(MsSql, self).__init__()

        self.mssql_ec2_instance = ec2.Instance(
            "Ec2Instance",
            ImageId=Ref(parameters.MssqlServerImageId),
            InstanceType=Ref(parameters.mssql_server_ec2_instance_type),
            KeyName=Ref(parameters.mssql_key_pair),
            SecurityGroupIds=[Ref(securitygroup.app_db_security_group)],
            UserData=Base64("80"),
            SubnetId=Ref(vpc.private_subnet_1),
            # VpcId=Ref(vpc.vpc)，
            # VPCZoneIdentifier=[Ref(vpc.private_subnet_1)],
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"),
                               " MsSql Servers"]),
                AutoSnapshot='1'
            ),
            PrivateIpAddress='10.215.3.135'
        )
