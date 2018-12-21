import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
ec2 = boto3.resource('ec2')
autoscaling = boto3.client('autoscaling')


def lambda_handler(event, context):
    # Use the filter() method of the instances collection to retrieve
    # all running EC2 instances.
    filters = [{
            'Name': 'tag:Replica',
            'Values': ['1']
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['running']
        }
    ]
    
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)

    #locate all running instances
    RunningInstances = [instance.id for instance in instances]
    
    # autoscaling.set_desired_capacity(
    #     AutoScalingGroupName='kis-RdpServerAutoscalingGroup-CLPKZ3MM4BET',
    #     DesiredCapacity=0,
    #     HonorCooldown=False
    # )
    #print the instances for logging purposes
    #print RunningInstances 
    
    #make sure there are actually instances to shut down. 
    if len(RunningInstances) > 0:
        #perform the shutdown
        shuttingDown = ec2.instances.filter(InstanceIds=RunningInstances).stop()
        print shuttingDown
    else:
        print "Nothing to see here"  