
$count=query user |  findstr ismarter | find /c "运行中 "
#$ip=get-WmiObject Win32_NetworkAdapterConfiguration|Where {$_.Ipaddress.length -gt 1} 
#$ip=$ip.ipaddress[0]
$ip=Invoke-RestMethod http://169.254.169.254/latest/meta-data/public-ipv4
$id=Invoke-RestMethod http://169.254.169.254/latest/meta-data/instance-id
echo $count
echo $ip
echo $instance_id
echo "appUsers=$ip,InstanceID=$instance_id"

$tags = aws ec2 describe-tags --filters "Name=resource-id,Values=${instance_id}" --region cn-north-1 --output=text | findStr 'PID' 
echo $tags
$produceId = (${tags} -split"\s+")[4]
aws cloudwatch put-metric-data --region cn-north-1 --metric-name OnLineCount --namespace UserCount --value $count --dimensions "produceId=$produceId"
aws cloudwatch put-metric-data --region cn-north-1 --metric-name OnLineCount --namespace UserCount --value $count --dimensions "produceId=$produceId,IP=$ip,InstanceID=$id"