from troposphere import Base64, Join, GetAZs, Tags, Select
from troposphere import Parameter, Ref, Template
from troposphere import cloudformation, autoscaling
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from magicdict import MagicDict




class AutoScaling(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(AutoScaling, self).__init__()

        self.launchConfig = LaunchConfiguration(
            "LaunchConfiguration",
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
            ImageId=Ref(parameters.RdpServerImageId),
            KeyName=Ref(parameters.key_pair),
            BlockDeviceMappings=[
                ec2.BlockDeviceMapping(
                    DeviceName="/dev/sda1",
                    Ebs=ec2.EBSBlockDevice(
                        VolumeSize="100"
                    )
                ),
            ],
            SecurityGroups=[
                Ref(securitygroup.app_rdp_instance_security_group)],
            InstanceType=Ref(parameters.rdp_server_ec2_instance_type),
        )
        self.AutoscalingGroup = AutoScalingGroup(
            "RdpAutoscalingGroup",
            DesiredCapacity=Ref(parameters.ScaleCapacity),
            Tags=Tags(
                Name=Join("-", [Ref("AWS::StackName"), "rdp-autoScaling"]),
            ),

            LaunchConfigurationName=Ref(self.launchConfig),
            MinSize=Ref(parameters.ScaleCapacity),
            MaxSize=Ref(parameters.ScaleCapacity),
            VPCZoneIdentifier=[Ref(vpc.private_subnet_1),
                               Ref(vpc.private_subnet_2)],
            # LoadBalancerNames=[Ref(LoadBalancer)],
            AvailabilityZones=[Ref(Select(0, GetAZs())),
                               Ref(Select(1, GetAZs()))],
            HealthCheckType="EC2",
            UpdatePolicy=UpdatePolicy(
                AutoScalingReplacingUpdate=AutoScalingReplacingUpdate(
                    WillReplace=True,
                ),
                AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                    PauseTime='PT5M',
                    MinInstancesInService="1",
                    MaxBatchSize='1',
                    WaitOnResourceSignals=True
                )
            )
        )
