from __future__ import print_function

import json
import boto3

from datetime import datetime, time

print('Loading function')
ec2 = boto3.client('ec2')


def lambda_handler(event, context):
    
    
    #print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print("Received event: " + message)
    snsMsg = json.loads(message)['Trigger']['Dimensions']
    
    for i in snsMsg:
        if i['name'] == 'InstanceID':
            instanceId = i['value']
        if i['name'] == 'IP':
            ip = i['value']
        print(i)
          # print(i)
    print(instanceId)
    print(ip)
    ec2.stop_instances(InstanceIds=[instanceId])
    return message
