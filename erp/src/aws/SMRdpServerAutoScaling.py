from troposphere import Base64, Join, GetAZs, Tags, Select
from troposphere import Parameter, Ref, Template
from troposphere import cloudformation, autoscaling
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.autoscaling import ScheduledAction
from troposphere.autoscaling import ScalingPolicy
from troposphere.autoscaling import StepAdjustments
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb
from magicdict import MagicDict
from troposphere.cloudwatch import Alarm, MetricDimension


class SMRdpServerAutoScaling(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(SMRdpServerAutoScaling, self).__init__()

        self.launchConfig = LaunchConfiguration(
            "SMRdpServerLaunchConfiguration",
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
            ImageId=Ref(parameters.SMRdpServerImageId),
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
            InstanceType=Ref(parameters.sm_rdp_server_ec2_instance_type),
            AssociatePublicIpAddress=False
        )
        self.AutoscalingGroup = AutoScalingGroup(
            "SmRdpServerAutoscalingGroup",
            DesiredCapacity=Ref(parameters.ScaleCapacity),
            Tags=[
                {
                    'Key': 'Name',
                    'Value': Join("-", [Ref("AWS::StackName"), "sm-rdp-server-autoScaling"]),
                    'PropagateAtLaunch':'true'
                },
                {
                    'Key': 'PID',
                    'Value': 'SM',
                    'PropagateAtLaunch': 'true'
                },
                {
                    'Key': 'Replica',
                    'Value': '1',
                    'PropagateAtLaunch': 'true'
                }
                # Name=Join("-", [Ref("AWS::StackName"), "rdp-server-autoScaling"]),
            ],

            LaunchConfigurationName=Ref(self.launchConfig),
            MinSize=Ref(parameters.MinCapacity),
            MaxSize=Ref(parameters.MaxCapacity),
            VPCZoneIdentifier=[Ref(vpc.public_subnet_7),
                               Ref(vpc.public_subnet_8)],
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

        self.start = ScheduledAction(
            "smSet2instancesAt8AM",
            AutoScalingGroupName=Ref(self.AutoscalingGroup),
            DesiredCapacity=2,
            Recurrence="10 0 * * MON-FRI"
        )

        self.end = ScheduledAction(
            "smSet1InstancesAt0AM",
            AutoScalingGroupName=Ref(self.AutoscalingGroup),
            DesiredCapacity=1,
            Recurrence="0 16 * * MON-FRI"
        )

        self.policy = ScalingPolicy(
            "smScalingOut",
            AutoScalingGroupName=Ref(self.AutoscalingGroup),
            PolicyType="StepScaling",
            AdjustmentType="ChangeInCapacity",
            StepAdjustments=[StepAdjustments(
                "ScaleOutSM",
                MetricIntervalLowerBound=0,
                ScalingAdjustment=1
            )]
        )

        self.outAlarm = Alarm(
            "smOutAlarm",
            MetricName = "OnLineCount",
            Namespace = "UserCount",
            AlarmName = "ScaleOut-SM",
            Dimensions = [
                MetricDimension(
                    Name = 'produceId',
                    Value = "SM"
                )],
            Period = 60,
            Statistic = "Average",
            EvaluationPeriods = 1,
            AlarmActions = [Ref(self.policy)],
            ComparisonOperator= "GreaterThanOrEqualToThreshold",
            Threshold = "20"
        )
