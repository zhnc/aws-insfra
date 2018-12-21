from troposphere import Base64, Join, GetAZs, Tags, Select,GetAtt
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

from troposphere.events import Rule, Target
from troposphere.awslambda import Permission



class HAUEServerAutoScaling(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(HAUEServerAutoScaling, self).__init__()

        self.launchConfig = LaunchConfiguration(
            "HAUEServerLaunchConfiguration",
            Metadata=autoscaling.Metadata(
                cloudformation.Init({
                    "config": cloudformation.InitConfig(     
                    )
                })
            ),
           
            ImageId=Ref(parameters.HAUEServerImageId),
            KeyName=Ref(parameters.rdp_server_key_pair),
            IamInstanceProfile="ec2-log-role",
            SecurityGroups=[
                Ref(securitygroup.app_ha_instance_security_group)],
            InstanceType=Ref(parameters.ha_server_ec2_instance_type),
            AssociatePublicIpAddress=True
        )
        self.AutoscalingGroup = AutoScalingGroup(
            "HAUEServerAutoscalingGroup",
            DesiredCapacity=1,#Ref(parameters.ScaleCapacity),
            Tags=[
                {
                    'Key' : 'Name',
                    'Value' : Join("-", [Ref("AWS::StackName"), "ha-ue-autoScaling"]),
                    'PropagateAtLaunch':'true'
                },
                {
                    'Key' : 'PID',
                    'Value' : 'HA-UE',
                    'PropagateAtLaunch':'true'
                }
                # Name=Join("-", [Ref("AWS::StackName"), "rdp-server-autoScaling"]),
            ],

            LaunchConfigurationName=Ref(self.launchConfig),
            MinSize=1,#Ref(parameters.MinCapacity),
            MaxSize=2,#Ref(parameters.MaxCapacity),
            VPCZoneIdentifier=[Ref(vpc.ha_subnet_1),
                               Ref(vpc.ha_subnet_2)],
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


        self.rule = Rule(
            "HAUE",
            Name="HAUEEIP",
            Description = "HA UE EIP",
            Targets=[Target(
                "smEipLambda",
                Arn = "arn:aws-cn:lambda:cn-northwest-1:926748824711:function:kis-HAProxy-EIP",
                Id = "HAUEEIP"
            )],
            EventPattern = {
                "source": [
                    "aws.autoscaling"
                    ],
                "detail-type": [
                    "EC2 Instance Launch Successful"
                ],
                "detail": {
                    "AutoScalingGroupName": [
                        Ref(self.AutoscalingGroup)
                    ]}
                }
        )

        self.Permission = Permission(
            "uelambda",
            Action="lambda:InvokeFunction",
            FunctionName = "arn:aws-cn:lambda:cn-northwest-1:926748824711:function:kis-HAProxy-EIP",
            Principal = "events.amazonaws.com",
            SourceArn = GetAtt(self.rule, 'Arn')
        )
