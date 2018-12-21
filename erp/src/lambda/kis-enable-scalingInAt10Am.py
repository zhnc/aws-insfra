import json
import boto3

cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    cloudwatch.enable_alarm_actions(
        AlarmNames=[
            'ScalingIn-UE','ScalingIn-PRO','ScalingIn-SM'
        ]
    )
    cloudwatch.set_alarm_state(
        AlarmName='ScalingIn-UE',
        StateValue='OK',
        StateReason='enable_alarm_actions'
    )
    cloudwatch.set_alarm_state(
        AlarmName='ScalingIn-PRO',
        StateValue='OK',
        StateReason='enable_alarm_actions'
    )
    cloudwatch.set_alarm_state(
        AlarmName='ScalingIn-SM',
        StateValue='OK',
        StateReason='enable_alarm_actions'
    )
    
    
    # TODO implement
    return {
        
    }
