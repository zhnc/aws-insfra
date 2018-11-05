from troposphere import Base64, Join
from troposphere import Ref, Template
from troposphere import GetAZs, Select, Tags
from troposphere.cloudformation import Init, InitConfig, InitFiles, InitFile
from troposphere.cloudformation import InitServices, InitService
from troposphere.iam import PolicyType
from troposphere.autoscaling import LaunchConfiguration
from troposphere.iam import Role
from troposphere.ecs import Cluster
from troposphere.autoscaling import AutoScalingGroup, Metadata
from troposphere.iam import InstanceProfile
from troposphere.ecr import Repository
from magicdict import MagicDict

from troposphere import Parameter, Ref, Template
from troposphere.ecs import (
    Cluster, Service, TaskDefinition,
    ContainerDefinition, NetworkConfiguration,
    AwsvpcConfiguration, PortMapping
)


class ECS(MagicDict):
    def __init__(self, vpc, parameters, securitygroup):
        """
        :type vpc VPC
        :type parameters Parameters
        :type securitygroup SecurityGroup
        """
        super(ECS, self).__init__()

        self.policyEcr = PolicyType(
            'PolicyEcr',
            PolicyName='EcrPolicy',
            PolicyDocument={'Version': '2012-10-17',
                            'Statement': [{'Action': ['ecr:GetAuthorizationToken'],
                                           'Resource': ['*'],
                                           'Effect': 'Allow'},
                                          {'Action': ['ecr:GetDownloadUrlForLayer',
                                                      'ecr:BatchGetImage',
                                                      'ecr:BatchCheckLayerAvailability'
                                                      ],
                                           'Resource': [
                                              '*'],
                                           'Effect': 'Allow',
                                           'Sid': 'AllowPull'},
                                          ]},
            Roles=[Ref('EcsClusterRole')],
        )

        self.policyEcs = PolicyType(
            'PolicyEcs',
            PolicyName='EcsPolicy',
            PolicyDocument={'Version': '2012-10-17',
                            'Statement': [
                                {'Action': ['ecs:CreateCluster',
                                            'ecs:RegisterContainerInstance',
                                            'ecs:DeregisterContainerInstance',
                                            'ecs:DiscoverPollEndpoint',
                                            'ecs:Submit*',
                                            'ecs:Poll',
                                            'ecs:StartTelemetrySession'],
                                 'Resource': '*',
                                 'Effect': 'Allow'}
                            ]},
            Roles=[Ref('EcsClusterRole')],
        )

        self.policyCloudwatch = PolicyType(
            'PolicyCloudwatch',
            PolicyName='Cloudwatch',
            PolicyDocument={'Version': '2012-10-17',
                            'Statement': [{'Action': ['cloudwatch:*'], 'Resource': '*',
                                           'Effect': 'Allow'}]},
            Roles=[Ref('EcsClusterRole')],
        )

        self.ECSCluster = Cluster(
            'ECSCluster',
        )

        self.containerInstances = LaunchConfiguration(
            'ContainerInstances',
            Metadata=Metadata(
                Init({
                    'config': InitConfig(
                        files=InitFiles({
                            '/etc/cfn/cfn-hup.conf': InitFile(
                                content=Join('', ['[main]\n', 'stack=', Ref('AWS::StackId'),  # NOQA
                                                '\n', 'region=', Ref('AWS::Region'), '\n']),  # NOQA
                                mode='000400',
                                owner='root',
                                group='root'
                            ),
                            '/etc/cfn/hooks.d/cfn-auto-reloader.conf': InitFile(
                                content=Join('', ['[cfn-auto-reloader-hook]\n',
                                                'triggers=post.update\n',
                                                'path=Resources.ContainerInstances.Metadata.AWS::CloudFormation::Init\n',  # NOQA
                                                'action=/opt/aws/bin/cfn-init -v ', '--stack ', Ref(  # NOQA
                                                    'AWS::StackName'), ' --resource ContainerInstances ', ' --region ', Ref('AWS::Region'), '\n',  # NOQA
                                                'runas=root\n']),
                                mode='000400',
                                owner='root',
                                group='root'
                            )},
                        ),
                        services=InitServices({
                            'cfn-hup': InitService(
                                ensureRunning='true',
                                enabled='true',
                                files=['/etc/cfn/cfn-hup.conf',
                                    '/etc/cfn/hooks.d/cfn-auto-reloader.conf']
                            )}
                        ),
                        commands={
                            '01_add_instance_to_cluster': {'command': Join('',
                                                                        ['#!/bin/bash\n',  # NOQA
                                                                            'echo ECS_CLUSTER=',  # NOQA
                                                                            # Ref(self.ECSCluster),# NOQA
                                                                            Ref('ECSCluster'),  # NOQA
                                                                            ' >> /etc/ecs/ecs.config'])}  # NOQA
                        }
                    )
                }
                ),
            ),
            UserData=Base64(Join('',
                                ['#!/bin/bash -xe\n',
                                'yum install -y aws-cfn-bootstrap\n',
                                '/opt/aws/bin/cfn-init -v ',
                                '         --stack ',
                                Ref('AWS::StackName'),
                                    '         --resource ContainerInstances ',
                                    '         --region ',
                                    Ref('AWS::Region'),
                                    '\n',
                                    '/opt/aws/bin/cfn-signal -e $? ',
                                    '         --stack ',
                                    Ref('AWS::StackName'),
                                    '         --resource ECSAutoScalingGroup ',
                                    '         --region ',
                                    Ref('AWS::Region'),
                                    '\n'])),
            ImageId=Ref(parameters.ECSImageId),
            KeyName=Ref(parameters.key_pair),
            SecurityGroups=[Ref(securitygroup.instance_security_group)],
            # IamInstanceProfile=Ref(self.EC2InstanceProfile),
            IamInstanceProfile=Ref('EC2InstanceProfile'),
            InstanceType=Ref(parameters.ec2_instance_type),
            AssociatePublicIpAddress='true',
            DependsOn=self.ECSCluster
        )

        self.ECSAutoScalingGroup = AutoScalingGroup(
            'ECSAutoScalingGroup',
            DesiredCapacity='1',
            MinSize='1',
            MaxSize='1',
            VPCZoneIdentifier=[Ref(vpc.public_subnet_1), Ref(
                vpc.public_subnet_2), Ref(vpc.public_subnet_3)],
            AvailabilityZones=[Select(0, GetAZs()), Select(
                1, GetAZs()), Select(2, GetAZs())],
            # LaunchConfigurationName=Ref(self.ContainerInstances),
            LaunchConfigurationName=Ref("ContainerInstances"),

        )

        self.EcsClusterRole = Role(
            'EcsClusterRole',
            Path='/',
            AssumeRolePolicyDocument={'Version': '2012-10-17',
                                      'Statement': [{'Action': 'sts:AssumeRole',
                                                     'Principal':
                                                     {'Service': 'ec2.amazonaws.com.cn'},
                                                     'Effect': 'Allow',
                                                     }]}
        )

        self.EC2InstanceProfile = InstanceProfile(
            'EC2InstanceProfile',
            Path='/',
            Roles=[Ref("EcsClusterRole")],
            DependsOn=self.EcsClusterRole
        )

        self.Repository = Repository(
            'MyRepository',
            RepositoryName='test-repository'
        )

        self.task_definition = TaskDefinition(
            'TaskDefinition',
            RequiresCompatibilities=['EC2'],
            Cpu='256',
            Memory='512',
            ContainerDefinitions=[
                ContainerDefinition(
                    Name='nginx',
                    # Image=Ref(self.Repository),
                    Image=Join ( ".", [ Ref ("AWS::AccountId"), "dkr.ecr", Ref ("AWS::Region"), Join ("/", [ "amazonaws.com", Ref (self.Repository ) ] ) ] ),
                    Essential=True,
                    PortMappings=[PortMapping(ContainerPort=80)]
                )
            ]
        )

        # self.service = Service(
        #     'NginxService',
        #     Cluster=Ref(self.ECSCluster ),
        #     DesiredCount=1,
        #     TaskDefinition=Ref(self.task_definition),
        #     LaunchType='EC2',
        #     NetworkConfiguration=NetworkConfiguration(
        #         AwsvpcConfiguration=AwsvpcConfiguration(
        #             Subnets=[Ref(vpc.public_subnet_1), Ref(
        #         vpc.public_subnet_2), Ref(vpc.public_subnet_3)]
        #         )
        #     )
        # )
