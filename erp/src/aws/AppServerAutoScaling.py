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


class AppServerAutoScaling(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(AppServerAutoScaling, self).__init__()

        self.loadBalancer = LoadBalancer(
            "LoadBalancer",

            Subnets=[Ref(vpc.private_subnet_1),
                     Ref(vpc.private_subnet_2)],
            # SubnetMappings=[],
            # HealthCheck=elb.HealthCheck(
            #     Target="HTTP:80/",
            #     HealthyThreshold="5",
            #     UnhealthyThreshold="2",
            #     Interval="20",
            #     Timeout="15",
            # ),
            # Listeners=[
            #     elb.Listener(
            #         InstancePort="80",
            #         InstanceProtocol="HTTP",
            #     ),
            # ],
            # CrossZone=True,
            SecurityGroups=[
                Ref(securitygroup.app_web_private_lb_security_group)],
            Name="app-api-lb",
            Scheme="internal",
            Type="application",
            # LoadBalancerPort=80
        )

        self.targetGroup = TargetGroup(
            "AppApiTargetGroupApi",
            HealthCheckIntervalSeconds="30",
            HealthCheckProtocol="HTTP",
            HealthCheckTimeoutSeconds="10",
            HealthyThresholdCount="4",
            Matcher=Matcher(
                HttpCode="200"),
            Name="AppApiTarget",
            Port=Ref(parameters.app_api_port),
            Protocol="HTTP",
            # Targets=[elb.TargetDescription(
            #     Id=Ref(ApiInstance),
            #     Port=Ref(apiport_param))],
            UnhealthyThresholdCount="3",
            VpcId=Ref(vpc.vpc)

        )

        self.listener = Listener(
            "Listener",
            Port="80",
            Protocol="HTTP",
            LoadBalancerArn=Ref(self.loadBalancer),
            DefaultActions=[Action(
                Type="forward",
                TargetGroupArn=Ref(self.targetGroup)
            )]
        )

        self.listener1 = Listener(
            "Listener1",
            Port="8288",
            Protocol="HTTP",
            LoadBalancerArn=Ref(self.loadBalancer),
            DefaultActions=[Action(
                Type="forward",
                TargetGroupArn=Ref(self.targetGroup)
            )]
        )

        self.listener2 = Listener(
            "Listener2",
            Port="3389",
            Protocol="HTTP",
            LoadBalancerArn=Ref(self.loadBalancer),
            DefaultActions=[Action(
                Type="forward",
                TargetGroupArn=Ref(self.targetGroup)
            )]
        )

        # template.add_resource(elb.ListenerRule(
        #     "ListenerRuleApi",
        #     ListenerArn=Ref(Listener),
        #     Conditions=[elb.Condition(
        #         Field="path-pattern",
        #         Values=["/api/*"])],
        #     Actions=[elb.Action(
        #         Type="forward",
        #         TargetGroupArn=Ref(TargetGroupApi)
        #     )],
        #     Priority="1"
        # ))

        self.launchConfig = LaunchConfiguration(
            "AppServerLaunchConfiguration",
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
            ImageId=Ref(parameters.AppServerImageId),
            KeyName=Ref(parameters.app_server_key_pair),
            BlockDeviceMappings=[
                ec2.BlockDeviceMapping(
                    DeviceName="/dev/sda1",
                    Ebs=ec2.EBSBlockDevice(
                        VolumeSize="100"
                    )
                ),
            ],
            SecurityGroups=[
                Ref(securitygroup.app_web_instance_security_group)],
            InstanceType=Ref(parameters.app_server_ec2_instance_type),
        )
        self.AutoscalingGroup = AutoScalingGroup(
            "AppServerAutoscalingGroup",
            DesiredCapacity=Ref(parameters.ScaleCapacity),
            Tags=[
                {
                    'Key': 'Name',
                    'Value': Join("-", [Ref("AWS::StackName"), "app-server-autoScaling"]),
                    'PropagateAtLaunch':'true'
                }
                # Name=Join("-", [Ref("AWS::StackName"), "rdp-server-autoScaling"]),
            ],

            LaunchConfigurationName=Ref(self.launchConfig),
            MinSize=Ref(parameters.ScaleCapacity),
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
