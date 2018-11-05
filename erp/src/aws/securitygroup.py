from troposphere import GetAtt, Join, Ref, Tags
from troposphere import ec2
import troposphere.elasticloadbalancingv2 as elb

from magicdict import MagicDict
from vpc import VPC


class SecurityGroup(MagicDict):
    def __init__(self, vpc):
        """
        :type vpc VPC
        """
        super(SecurityGroup, self).__init__()

        # web
        self.load_balancer_security_group = ec2.SecurityGroup(
            "LoadBalancerSecurityGroup",
            GroupDescription="Loadbalancer security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=80,
                    ToPort=80,
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=443,
                    ToPort=443,
                    CidrIp="0.0.0.0/0",
                )
            ],
            SecurityGroupEgress=[
                ec2.SecurityGroupRule(
                    CidrIp="0.0.0.0/0",
                    FromPort=0,
                    IpProtocol="-1",
                    ToPort=65535
                )
            ],
            VpcId=Ref(vpc.vpc),
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"),
                               " load balancer security group"]),
            ),
        )

        # EC2 instance security group
        self.instance_security_group = ec2.SecurityGroup(
            "InstanceSecurityGroup",
            GroupDescription="Instance security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    # SourceSecurityGroupId=GetAtt(
                    #     self.load_balancer_security_group, "GroupId"),
                    SourceSecurityGroupId=Ref(self.load_balancer_security_group)
                )
            ],
            SecurityGroupEgress=[
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    CidrIp="0.0.0.0/0",
                ),
            ],
            VpcId=Ref(vpc.vpc),
            Tags=Tags(
                Name=Join("", [Ref("AWS::StackName"),
                               " instance security group"]),
            ),
        )

        self.instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "instanceSecurityGroupIngressRule",
            GroupId=Ref(self.instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.instance_security_group
        )
