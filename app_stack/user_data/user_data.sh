#!/bin/bash -xe

# to send user-data output(logs) to be able to fetch 
# on the console(ec2 > instances > Actions > Monitor and troubleshoot > Get System Log) 
# https://aws.amazon.com/ko/premiumsupport/knowledge-center/ec2-linux-log-user-data/

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
  echo "yum update"
  yum -y update
  echo "yum install ssm-agent"
  sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
