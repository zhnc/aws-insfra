it is a project that help to build the aws insfra for XXX.
This project use python generate the AWS Cloudformation that contains VPC, AppServerAutoScaling, HAProxyAutoScaling, RdpProductAutoScaling, CloudWatch Metrics to monitor app cluster and trigger Lambda to auto maintain the cluster.

## Use below command to install dependency.

pip3 install -r requirements.txt

## Useful commands

 * `make all`             generate AWS Cloudformation resource 
 * `clean`                clean resouce 
