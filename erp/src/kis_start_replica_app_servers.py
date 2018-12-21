import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
ec2 = boto3.resource('ec2')
cloudwatch = boto3.client('cloudwatch')
autoscaling = boto3.client('autoscaling')

def lambda_handler(event, context):
    
    cloudwatch.disable_alarm_actions(
        AlarmNames=[
            'ScalingInUE','ScalingInPro','ScalingInSM'
        ]
    )
  

    
    # Use the filter() method of the instances collection to retrieve
    # all running EC2 instances.
    filters = [{
            'Name': 'tag:Replica',
            'Values': ['1']
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['stopped']
        }
    ]
    
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)

    #locate all stopped instances
    StoppedInstances = [instance.id for instance in instances]
    
    
    #make sure there are actually instances to start. 
    if len(StoppedInstances) > 0:
        #perform the startup
        startingUp = ec2.instances.filter(InstanceIds=StoppedInstances).start()
        print startingUp
    else:
        print "Nothing to see here"