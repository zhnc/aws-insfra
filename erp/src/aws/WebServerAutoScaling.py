from troposphere import Base64, Join, GetAZs, Tags, Select
from troposphere import Parameter, Ref, Template
from troposphere import cloudformation, autoscaling
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancingv2 import LoadBalancer, TargetGroup, Matcher, Listener, Action
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from magicdict import MagicDict


class WebServerAutoScaling(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(WebServerAutoScaling, self).__init__()

        self.loadBalancer = LoadBalancer(
            "WebLoadBalancer",

            Subnets=[Ref(vpc.public_subnet_1),
                     Ref(vpc.public_subnet_2)],
            SecurityGroups=[
                Ref(securitygroup.web_public_security_group)],
            Name="web-lb",
            Scheme="internet-facing",
            Type="application",
            
        )

        self.targetGroup = TargetGroup(
            "WebTargetGroupApi",
            HealthCheckIntervalSeconds="30",
            HealthCheckProtocol="HTTP",
            HealthCheckTimeoutSeconds="10",
            HealthyThresholdCount="4",
            Matcher=Matcher(
                HttpCode="200"),
            Name="WebTarget",
            Port=Ref(parameters.web_port),
            Protocol="HTTP",
            UnhealthyThresholdCount="3",
            VpcId=Ref(vpc.vpc),
            HealthCheckPath="/favicon.ico"

        )

        self.listener = Listener(
            "WebListener",
            Port="8088",
            Protocol="HTTP",
            LoadBalancerArn=Ref(self.loadBalancer),
            DefaultActions=[Action(
                Type="forward",
                TargetGroupArn=Ref(self.targetGroup)
            )]
        )

        self.listener1 = Listener(
            "WebListener1",
            Port="3306",
            Protocol="HTTP",
            LoadBalancerArn=Ref(self.loadBalancer),
            DefaultActions=[Action(
                Type="forward",
                TargetGroupArn=Ref(self.targetGroup)
            )]
        )

        self.launchConfig = LaunchConfiguration(
            "WebServerLaunchConfiguration",
            Metadata=autoscaling.Metadata(
                cloudformation.Init({
                    "config": cloudformation.InitConfig(
                        # files=cloudformation.InitFiles({
                        #     "/etc/rsyslog.d/20-somethin.conf": cloudformation.InitFile(
                        #         source=Join('', [
                        #             "http://",
                        #             Ref(DeployBucket),
                        #             ".s3.amazonaws.com/stacks/",
                        #             Ref(RootStackName),
                        #             "/env/etc/rsyslog.d/20-somethin.conf"
                        #         ]),
                        #         mode="000644",
                        #         owner="root",
                        #         group="root",
                        #         authentication="DeployUserAuth"
                        #     )
                        # }),
                        # services={
                        #     "sysvinit": cloudformation.InitServices({
                        #         "rsyslog": cloudformation.InitService(
                        #             enabled=True,
                        #             ensureRunning=True,
                        #             files=['/etc/rsyslog.d/20-somethin.conf']
                        #         )
                        #     })
                        # }
                    )
                })
                # ,
                # cloudformation.Authentication({
                #     "DeployUserAuth": cloudformation.AuthenticationBlock(
                #         type="S3",
                #         accessKeyId=Ref(DeployUserAccessKey),
                #         secretKey=Ref(DeployUserSecretKey)
                #     )
                # })
            ),
            # UserData=Base64(Join('', [
            #     "#!/bin/bash\n",
            #     "cfn-signal -e 0",
            #     "    --resource AutoscalingGroup",
            #     "    --stack ", Ref("AWS::StackName"),
            #     "    --region ", Ref("AWS::Region"), "\n"
            # ])),
            ImageId=Ref(parameters.WebPortalServerImageId),
            KeyName=Ref(parameters.web_server_key_pair),
            BlockDeviceMappings=[
                ec2.BlockDeviceMapping(
                    DeviceName="/dev/sdb",
                    Ebs=ec2.EBSBlockDevice(
                        VolumeSize="200",
                        VolumeType="gp2"
                    )
                ),
            ],
            SecurityGroups=[
                Ref(securitygroup.web_instance_security_group)],
            InstanceType=Ref(parameters.web_server_ec2_instance_type),
        )
        self.AutoscalingGroup = AutoScalingGroup(
            "WebServerAutoscalingGroup",
            DesiredCapacity= 0, #Ref(parameters.ScaleCapacity),
            Tags=[
                {
                    'Key': 'Name',
                    'Value': Join("-", [Ref("AWS::StackName"), "web-server-autoScaling"]),
                    'PropagateAtLaunch':'true'
                }
                # Name=Join("-", [Ref("AWS::StackName"), "rdp-server-autoScaling"]),
            ],

            LaunchConfigurationName=Ref(self.launchConfig),
            MinSize=Ref(parameters.MinCapacity),
            MaxSize=Ref(parameters.ScaleCapacity),
            VPCZoneIdentifier=[Ref(vpc.private_subnet_1),
                               Ref(vpc.private_subnet_2)],
            # LoadBalancerNames=[Ref(self.loadBalancer)],
            TargetGroupARNs=[Ref(self.targetGroup)],
            AvailabilityZones=[Select(0, GetAZs()),
                               Select(1, GetAZs())],
            HealthCheckType="EC2",
            HealthCheckGracePeriod=300,
            UpdatePolicy=UpdatePolicy(
                AutoScalingReplacingUpdate=AutoScalingReplacingUpdate(
                    WillReplace=True,
                ),
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT5M',
                    MinInstancesInService="1",
                    MaxBatchSize='1',
                    WaitOnResourceSignals=True
                ),
            )
        )
