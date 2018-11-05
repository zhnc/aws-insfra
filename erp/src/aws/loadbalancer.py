from troposphere import GetAtt, Join, Ref, Tags
from troposphere import ec2
import troposphere.elasticloadbalancingv2 as elb

from magicdict import MagicDict
from vpc import VPC
from securitygroup import SecurityGroup
from parameters import Parameters



class LoadBalancer(MagicDict):
    def __init__(self, vpc,parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(LoadBalancer, self).__init__()

        self.load_balancer = elb.LoadBalancer(
            "ApplicationElasticLB",
            Name="ApplicationElasticLB",
            Scheme="internal",
            Subnets=[Ref(vpc.public_subnet_1), Ref(
                vpc.public_subnet_2)],
            SecurityGroups=[
                GetAtt(securitygroup.web_public_security_group, "GroupId"),
            ],
            DependsOn=vpc.internet_gateway_attachment.title
        )

        self.TargetGroupWeb = elb.TargetGroup(
            "TargetGroupWeb",
            HealthCheckIntervalSeconds="30",
            HealthCheckProtocol="HTTP",
            HealthCheckTimeoutSeconds="10",
            HealthyThresholdCount="4",
            Matcher=elb.Matcher(
                HttpCode="200"),
            Name="WebTarget",
            Port=Ref(parameters.WebServerPort),
            Protocol="HTTP",
            # Targets=[elb.TargetDescription(
            #     Id=Ref(WebInstance),
            #     Port=Ref(webport_param))],
            UnhealthyThresholdCount="3",
            VpcId=Ref(vpc.vpc)

        )

    
