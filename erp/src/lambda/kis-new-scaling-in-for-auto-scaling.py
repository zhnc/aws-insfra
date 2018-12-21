import boto3
import logging
import json
import datetime

autoscaling = boto3.client('autoscaling')
cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    
    message = event['Records'][0]['Sns']['Message']
    AlarmName = json.loads(message)['AlarmName']
    print(AlarmName)
    # print("Received event: " + message)
    snsMsg = json.loads(message)['Trigger']['Dimensions']
    for i in snsMsg:
        if i['name'] == 'produceId':
            produceId = i['value']
    
    print(produceId)
    groups = autoscaling.describe_auto_scaling_groups()


    for group in groups["AutoScalingGroups"]:
        if(group["AutoScalingGroupName"].find("RdpServerAutoscalingGroup") > -1) :
            # print(group["AutoScalingGroupName"])
            tags = group["Tags"]
            for tag in tags:
                if(tag["Key"] == "PID" and tag["Value"] == produceId):
                    AutoScalingGroupName = group["AutoScalingGroupName"]
                    DesiredCapacity = group["DesiredCapacity"]
                    Instances = group["Instances"]
    print(AutoScalingGroupName)
    print(DesiredCapacity)
    print(Instances)
    
    if(DesiredCapacity>1):
        currentTime = datetime.datetime.now()
        startTime = datetime.datetime.now() - datetime.timedelta(minutes = 5)
        for instance in Instances:
            metric = cloudwatch.get_metric_data(StartTime=startTime,EndTime=currentTime,MetricDataQueries=[{
                        'Id': 'xxx01',
                        'MetricStat': {'Metric': {'Namespace': 'UserCount','MetricName': 'OnLineCount',
                                'Dimensions': [
                                    {
                                        'Name': 'produceId',
                                        'Value': produceId
                                    },{
                                        'Name': 'InstanceID',
                                        'Value':instance['InstanceId']
                                    }
                                ]
                            },
                            'Period': 300,
                            'Stat': 'Sum'
                        },
                        'Label': 'lable0'
                    }])
            
            users = metric["MetricDataResults"][0]["Values"]
            # print(len(users))
            
            if len(users) > 0 and all(x == 0 for x in users) :
                #detach instances from group, and tenimate
                autoscaling.detach_instances(
                    InstanceIds=[
                        instance["InstanceId"],
                    ],
                    AutoScalingGroupName=AutoScalingGroupName,
                    ShouldDecrementDesiredCapacity=True
                )
                ec2.terminate_instances(
                    InstanceIds=[
                        instance["InstanceId"],
                    ]
                )
                cloudwatch.set_alarm_state(
                    AlarmName=AlarmName,
                    StateValue='OK',
                    StateReason='enable_alarm_actions'
                )
                return
            

            
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
