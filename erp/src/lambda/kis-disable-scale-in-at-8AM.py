import json
import boto3

cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    cloudwatch.disable_alarm_actions(
        AlarmNames=[
            'ScalingIn-UE','ScalingIn-PRO','ScalingIn-SM'
        ]
    )
   
    # TODO implement
    return {
        
    }
