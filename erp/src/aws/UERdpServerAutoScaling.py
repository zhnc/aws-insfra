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




class UERdpServerAutoScaling(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(UERdpServerAutoScaling, self).__init__()

        self.launchConfig = LaunchConfiguration(
            "UERdpServerLaunchConfiguration",
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
            ImageId=Ref(parameters.UERdpServerImageId),
            KeyName=Ref(parameters.rdp_server_key_pair),
            IamInstanceProfile="ec2-log-role",
            BlockDeviceMappings=[
                ec2.BlockDeviceMapping(
                    DeviceName="/dev/sda1",
                    Ebs=ec2.EBSBlockDevice(
                        VolumeSize="60",
                        VolumeType="gp2"
                    )
                )
            ],
            SecurityGroups=[
                Ref(securitygroup.app_rdp_instance_security_group)],
            InstanceType=Ref(parameters.ue_rdp_server_ec2_instance_type),
            AssociatePublicIpAddress=True
        )
        self.AutoscalingGroup = AutoScalingGroup(
            "UeRdpServerAutoscalingGroup",
            DesiredCapacity=Ref(parameters.ScaleCapacity),
            Tags=[
                {
                    'Key' : 'Name',
                    'Value' : Join("-", [Ref("AWS::StackName"), "ue-rdp-server-autoScaling"]),
                    'PropagateAtLaunch':'true'
                },
                {
                    'Key' : 'PID',
                    'Value' : 'UE',
                    'PropagateAtLaunch':'true'
                },
                {
                    'Key' : 'Replica',
                    'Value' : '1',
                    'PropagateAtLaunch':'true'
                }
                # Name=Join("-", [Ref("AWS::StackName"), "rdp-server-autoScaling"]),
            ],

            LaunchConfigurationName=Ref(self.launchConfig),
            MinSize=Ref(parameters.MinCapacity),
            MaxSize=Ref(parameters.ScaleCapacity),
            VPCZoneIdentifier=[Ref(vpc.public_subnet_1),
                               Ref(vpc.public_subnet_2)],
            # LoadBalancerNames=[Ref(LoadBalancer)],
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
