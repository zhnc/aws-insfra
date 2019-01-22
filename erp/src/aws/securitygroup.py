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

        # ops
        self.ops = ec2.SecurityGroup(
            "OpsSecurityGroup",
            GroupDescription="Ops security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=3389,
                    ToPort=3389,
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=22,
                    ToPort=22,
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
                               " ops security group"]),
            ),
        )

        # # client
        # self.client_security_group = ec2.SecurityGroup(
        #     "clientSecurityGroup",
        #     GroupDescription="client security group",
        #     SecurityGroupIngress=[
        #         ec2.SecurityGroupRule(
        #             IpProtocol="tcp",
        #             FromPort=3389,
        #             ToPort=3389,
        #             CidrIp="0.0.0.0/0",
        #         )
        #     ],
        #     SecurityGroupEgress=[
        #         ec2.SecurityGroupRule(
        #             CidrIp="0.0.0.0/0",
        #             FromPort=0,
        #             IpProtocol="-1",
        #             ToPort=65535
        #         )
        #     ],
        #     VpcId=Ref(vpc.vpc),
        #     Tags=Tags(
        #         Name=Join("", [Ref("AWS::StackName"),
        #                        " client security group"]),
        #     ),
        # )

        # web load balance
        # self.web_public_security_group = ec2.SecurityGroup(
        #     "WebPublicLoadBalanceSecurityGroup",
        #     GroupDescription="web public load balance security group",
        #     SecurityGroupIngress=[
        #         ec2.SecurityGroupRule(
        #             IpProtocol="tcp",
        #             FromPort=80,
        #             ToPort=80,
        #             CidrIp="0.0.0.0/0",
        #         ),
        #         ec2.SecurityGroupRule(
        #             IpProtocol="tcp",
        #             FromPort=443,
        #             ToPort=443,
        #             CidrIp="0.0.0.0/0",
        #         )
        #     ],
        #     SecurityGroupEgress=[
        #         ec2.SecurityGroupRule(
        #             CidrIp="0.0.0.0/0",
        #             FromPort=0,
        #             IpProtocol="-1",
        #             ToPort=65535
        #         )
        #     ],
        #     VpcId=Ref(vpc.vpc),
        #     Tags=Tags(
        #         Name=Join("", [Ref("AWS::StackName"),
        #                        " web public load balance security group"]),
        #     ),
        # )

        # Web EC2 instance security group
        self.web_instance_security_group = ec2.SecurityGroup(
            "WebInstanceSecurityGroup",
            GroupDescription="Web Instance security group",
            SecurityGroupIngress=[
               ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="80",
                    ToPort="81",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="5366",
                    ToPort="5367",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="3389",
                    ToPort="3389",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="ICMP",
                    FromPort="-1",
                    ToPort="-1",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    SourceSecurityGroupId=Ref(self.ops),
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
                               " web instance security group"]),
            ),
        )

        self.web_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "instanceSecurityGroupIngressRule",
            GroupId=Ref(self.web_instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.web_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.web_instance_security_group
        )

        
        
     


        

        
        #app service private security group

        self.app_instance_security_group = ec2.SecurityGroup(
            "AppInstanceSecurityGroup",
            GroupDescription="App Instance security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="80",
                    ToPort="81",
                    SourceSecurityGroupId=Ref(self.web_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="5366",
                    ToPort="5367",
                    SourceSecurityGroupId=Ref(self.web_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="3389",
                    ToPort="3389",
                    SourceSecurityGroupId=Ref(self.web_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="ICMP",
                    FromPort="-1",
                    ToPort="-1",
                    SourceSecurityGroupId=Ref(self.web_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    SourceSecurityGroupId=Ref(self.web_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    SourceSecurityGroupId=Ref(self.ops),
                ),
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
                               " App  instance security group"]),
            ),
        )

        # db security group

        self.db_security_group = ec2.SecurityGroup(
            "dBSecurityGroup",
            GroupDescription="DB security group",
            SecurityGroupIngress=[
                
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="1433",
                    ToPort="1433",
                    SourceSecurityGroupId=Ref(self.app_instance_security_group)
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="80",
                    ToPort="81",
                    SourceSecurityGroupId=Ref(self.app_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="5366",
                    ToPort="5367",
                    SourceSecurityGroupId=Ref(self.app_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="3389",
                    ToPort="3389",
                    SourceSecurityGroupId=Ref(self.app_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="ICMP",
                    FromPort="-1",
                    ToPort="-1",
                    SourceSecurityGroupId=Ref(self.app_instance_security_group),
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    SourceSecurityGroupId=Ref(self.ops),
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
                               " App DB security group"]),
            ),
        )


        #security ingress
        self.app_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "appInstanceSecurityGroupIngressRule",
            GroupId=Ref(self.app_instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.app_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.app_instance_security_group
        )

   

        self.web_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "webInstanceSecurityGroupIngressRule",
            GroupId=Ref(self.web_instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.web_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.web_instance_security_group
        )

        self.db_security_group_groupIngressRule = ec2.SecurityGroupIngress(
            "dbGroupIngressRule",
            GroupId=Ref(self.db_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.db_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.db_security_group
        )

       

      
        
        
