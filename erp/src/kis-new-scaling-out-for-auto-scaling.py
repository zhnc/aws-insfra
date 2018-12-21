import json
import time
import boto3

ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

def lambda_handler(event, context):
    instanceId = event["detail"]["EC2InstanceId"]
    augName = event["detail"]["AutoScalingGroupName"]
    tags = autoscaling.describe_tags(Filters=[{"Name":"auto-scaling-group","Values":[augName]}])

    produceId = [i for i in tags["Tags"] if i["Key"] == "PID"][0]["Value"]
    
    addresses = ec2.describe_addresses(Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                produceId
            ]
        },
    ])["Addresses"]
    
    allocationId = [i for i in addresses if 'InstanceId' not in i][0]['AllocationId']
    
    ec2.associate_address(AllocationId=allocationId,InstanceId=instanceId)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
