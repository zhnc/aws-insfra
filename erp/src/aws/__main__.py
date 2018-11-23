from troposphere import GetAtt, Output, Template

# from database import Database
# from ec2 import EC2
from loadbalancer import LoadBalancer
from mappings import Mappings
from parameters import Parameters
from vpc import VPC
from securitygroup import SecurityGroup
from ecs import ECS
from RdpServerAutoScaling import RdpServerAutoScaling
from AppServerAutoScaling import AppServerAutoScaling
from WebServerAutoScaling import WebServerAutoScaling

from mssql import MsSql


def main():
    template = Template()
    template.add_description("Example Server")

    for key, value in Mappings().mappings.items():
        template.add_mapping(key, value)

    parameters = Parameters()
    for param in parameters.values():
        template.add_parameter(param)

    template.add_metadata({
        "AWS::CloudFormation::Interface": {
            "ParameterGroups": [
                {
                    "Label": {
                        "default": "Required parameters."
                    },
                    "Parameters": [
                        "DBPassword",
                        "KeyPair",
                    ]
                },
                {
                    "Label": {
                        "default": "Advanced: Database and instance"
                    },
                    "Parameters": ["DBInstanceType", "DBStorageSize", "DBBackupRetention", "EC2InstanceType"]
                },
            ],
            "ParameterLabels": {
                "DBPassword": {"default": "Choose a database password"},
                "DBStorageSize": {"default": "Database storage (advanced)"},
                "DBBackupRetention": {"default": "How long to keep backups (advanced)"},
                "DBInstanceType": {"default": "Database instance class (advanced)"},
                "KeyPair": {"default": "Choose a key pair"},
                "EC2InstanceType": {"default": "Instance class (advanced)"},
            }
        }
    })

    vpc = VPC()
    for res in vpc.values():
        template.add_resource(res)

    securityGroup = SecurityGroup(vpc=vpc)
    for res in securityGroup.values():
        template.add_resource(res)

    rdpServerAutoScaling = RdpServerAutoScaling(vpc=vpc, parameters=parameters, securitygroup= securityGroup)
    for res in rdpServerAutoScaling.values():
        template.add_resource(res)

    appServerAutoScaling = AppServerAutoScaling(vpc=vpc, parameters=parameters, securitygroup= securityGroup)
    for res in appServerAutoScaling.values():
        template.add_resource(res)

        
    webServerAutoScaling = WebServerAutoScaling(vpc=vpc, parameters=parameters, securitygroup= securityGroup)
    for res in webServerAutoScaling.values():
        template.add_resource(res)
        
    mssql = MsSql(vpc=vpc, parameters=parameters, securitygroup= securityGroup)
    for res in mssql.values():
        template.add_resource(res)
        
    # elb = LoadBalancer(vpc=vpc, parameters=parameters, securitygroup= securityGroup)
    # for res in elb.values():
    #     template.add_resource(res)

    # ecs = ECS(vpc=vpc, parameters=parameters, securitygroup= securityGroup)
    # for res in ecs.values():
    #     template.add_resource(res)

    # db = Database(parameters=parameters, vpc=vpc, loadbalancer=elb)
    # for res in db.values():
    #     template.add_resource(res)

    # ec2 = EC2(parameters=parameters, vpc=vpc, loadbalancer=elb)
    # for res in ec2.values():
    #     template.add_resource(res)

    # template.add_output(Output(
    #     "LoadBalancerDNSName",
    #     Value=GetAtt(elb.load_balancer, "DNSName")
    # ))

    print(template.to_yaml())


if __name__ == "__main__":
    main()
