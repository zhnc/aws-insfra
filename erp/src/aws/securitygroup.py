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

        # web load balance
        self.web_public_security_group = ec2.SecurityGroup(
            "WebPublicLoadBalanceSecurityGroup",
            GroupDescription="web public load balance security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=80,
                    ToPort=80,
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=8088,
                    ToPort=8088,
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort=3306,
                    ToPort=3306,
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
                               " web public load balance security group"]),
            ),
        )

        # Web EC2 instance security group
        self.web_instance_security_group = ec2.SecurityGroup(
            "WebInstanceSecurityGroup",
            GroupDescription="Web Instance security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    # SourceSecurityGroupId=GetAtt(
                    #     self.load_balancer_security_group, "GroupId"),
                    SourceSecurityGroupId=Ref(self.web_public_security_group)
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

        
        # web db security group
        self.web_db_security_group = ec2.SecurityGroup(
            "WebDBSecurityGroup",
            GroupDescription="Web DB security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="3306",
                    ToPort="3306",
                    SourceSecurityGroupId=Ref(self.web_instance_security_group)
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
                               " web DB security group"]),
            ),
        )

        self.web_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "instanceSecurityGroupIngressRule",
            GroupId=Ref(self.web_instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.web_public_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.web_db_security_group
        )


        #app web private load balance

        self.app_web_private_lb_security_group = ec2.SecurityGroup(
            "AppWebPrivateLoadBalanceSecurityGroup",
            GroupDescription="App web private load balance security group",
            # SecurityGroupIngress=[
            #     ec2.SecurityGroupRule(
            #         IpProtocol="tcp",
            #         FromPort=80,
            #         ToPort=80,
            #         CidrIp="0.0.0.0/0",
            #     ),
            #     ec2.SecurityGroupRule(
            #         IpProtocol="tcp",
            #         FromPort=443,
            #         ToPort=443,
            #         CidrIp="0.0.0.0/0",
            #     )
            # ],
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
                               " App web private load balance security group"]),
            ),
        )

        #app web service private security group

        self.app_web_instance_security_group = ec2.SecurityGroup(
            "AppWebInstanceSecurityGroup",
            GroupDescription="App Web Instance security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="-1",
                    FromPort="-1",
                    ToPort="-1",
                    # SourceSecurityGroupId=GetAtt(
                    #     self.load_balancer_security_group, "GroupId"),
                    SourceSecurityGroupId=Ref(self.app_web_private_lb_security_group)
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
                               " App Web instance security group"]),
            ),
        )

        #app rdp service private security group

        self.app_rdp_instance_security_group = ec2.SecurityGroup(
            "AppRdpInstanceSecurityGroup",
            GroupDescription="App RDP Instance security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="8696",
                    ToPort="8696",
                    CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="5696",
                    ToPort="5696",
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
                               " App RDP instance security group"]),
            ),
        )

        #app db security group

        self.app_db_security_group = ec2.SecurityGroup(
            "AppDBSecurityGroup",
            GroupDescription="App DB security group",
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="1433",
                    ToPort="1433",
                    SourceSecurityGroupId=Ref(self.app_web_instance_security_group)
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="1433",
                    ToPort="1433",
                    SourceSecurityGroupId=Ref(self.app_rdp_instance_security_group)
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="55555",
                    ToPort="55555",
                    SourceSecurityGroupId=Ref(self.app_web_instance_security_group)
                ),
                ec2.SecurityGroupRule(
                    IpProtocol="tcp",
                    FromPort="55555",
                    ToPort="55555",
                    SourceSecurityGroupId=Ref(self.app_rdp_instance_security_group)
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
        self.app_rdp_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "appRdpInstanceSecurityGroupIngressRule",
            GroupId=Ref(self.app_rdp_instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.app_rdp_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.app_rdp_instance_security_group
        )
        
        self.app_web_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "appWebInstanceSecurityGroupIngressRule",
            GroupId=Ref(self.app_web_instance_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.app_web_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.app_web_instance_security_group
        )

        self.app_web_private_lb_security_groupIngressRule = ec2.SecurityGroupIngress(
            "appWebPrivateLbSecurityGroupIngressRule03",
            GroupId=Ref(self.app_web_private_lb_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.app_rdp_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.app_rdp_instance_security_group
        )

        self.web_instance_security_groupIngressRule = ec2.SecurityGroupIngress(
            "webInstanceSecurityGroupIngressRule",
            GroupId=Ref(self.app_web_private_lb_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.web_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.web_instance_security_group
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

        self.web_public_security_group_groupIngressRule = ec2.SecurityGroupIngress(
            "webPublicSecurityGroupIngressRule",
            GroupId=Ref(self.web_public_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.web_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.web_instance_security_group
        )

        self.app_web_private_lb_security_groupIngressRule01 = ec2.SecurityGroupIngress(
            "appApicSecurityGroupIngressRule01",
            GroupId=Ref(self.app_web_private_lb_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.ops),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.ops
        )

        self.app_web_private_lb_security_groupIngressRule02 = ec2.SecurityGroupIngress(
            "appApicSecurityGroupIngressRule02",
            GroupId=Ref(self.app_web_private_lb_security_group),
            IpProtocol='-1',
            SourceSecurityGroupId=Ref(self.web_instance_security_group),
            FromPort='-1',
            ToPort='-1',
            DependsOn=self.web_instance_security_group
        )

        # TODO:: iis security group 8288 to nlb
        
