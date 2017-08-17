# Skew Scripts

## About

The entertainment company [Scopely][Scopely] maintains a very useful library for
querying and indexing resources within AWS.  This repo is a collection of
scripts used for my own maintenance of AWS.  Most of them which output JSON
data are intended to grab an entire catalog of information for offline
processing with [JQ][JQ].

## Prerequisites

This scripts in this repo need [Skew][skew] to run.

## Notes

Some of the scripts here are mirrored from `garnaat`'s gists (noted 
[here][garnaat]).  They are tracked in this repo in the event that
modifications were/are made.

## Content

  - `asg.py`: Index information on autoscaling groups
  - `empty_vpc.py`: Get a list of empty VPCs
  - `inventory.py`: Generate a JSON index of commonly used AWS resources
  - `ipwhitelist.py`: Check for whitelisted IP ranges in security groups
  - `lost_volumes.py`: Find all orphaned EBS volumes
  - `snapshots.py`: Get a list of all AWS snapshots

## Processing Examples

In the examples below, some commads utilize the `AWS_PROFILE` variable.  You wil need top replace `example-profile` with the name of a profile from `~/.aws/credentials`.

After installing [Skew][skew] and creating the file `~/.skew`, begin by running the following scripts:

```
$ AWS_PROFILE=example-profile ./asg.py
$ AWS_PROFILE=example-profile ./inventory.py
```

After completing these commands, proceed with the following examples: 

### Generate commands for aws to describe all instances

```
jq -cr    '[.[]  | {"awsRegion": (.ARN | split(":") | .[3]), "InstanceId": .InstanceId, "Account": (.ARN | split(":") | .[4])} ]  | group_by(.Account) | .[1][] | @sh "aws --region \(.awsRegion) ec2 describe-instances --instance-ids \(.InstanceId)"  '  aws-ec2.json
```

### show all instances without the tags "createdBy" or "CreatedBy"

```
jq     ' .[] | del ( .  | select(.Tags[]?.Key == ("CreatedBy" or "createdBy")  ) )  '  aws-ec2.json
```

### Generate arrays of instances by account

show all autoscale group instances  which are missing the tag "createdBy".  from this list, extract the instances into an object, then group into an array by account:

```
jq '[.[] | del(select (.Tags[]?.Key  == "createdBy"  )) | {"InstanceId": .Instances[]?.InstanceId?, "ASG": .AutoScalingGroupName, "awsRegion": (.ARN | split(":") | .[3]), "Account": (.ARN | split(":") | .[4])}] | group_by(.Account) ' aws-asg.json
```


### delete all autoscaling groups missing the above tags:
notes:  it needs the autoscalinggroupname != null to not fail on the deleted entries

```
jq '[.[] | del(select (.Tags[]?.Key  == "createdBy" )) |  select(.AutoScalingGroupName != null) | {"ASG": .AutoScalingGroupName, "awsRegion": (.ARN | split(":") | .[3]), "Account": (.ARN | split(":") | .[4])}] | group_by(.Account)|  .[1][] | @sh "AWS_PROFILE=example-profile aws autoscaling delete-auto-scaling-group --auto-scaling-group-name \(.ASG) --region \(.awsRegion)" ' aws-asg.json
```

```
jq -r  '[.[] | del(select (.Tags[]?.Key  == "createdBy" )) |  select(.AutoScalingGroupName != null) | {"ASG": .AutoScalingGroupName, "awsRegion": (.ARN | split(":") | .[3]), "Account": (.ARN | split(":") | .[4])}] | group_by(.Account)|  .[1][] | @sh "AWS_PROFILE=example-profile aws autoscaling update-auto-scaling-group --auto-scaling-group-name \(.ASG) --region \(.awsRegion) --desired-capacity 0 --min-size 0 --default-cooldown 2" ' aws-asg.json
```

```
jq -r  '[.[] | del(select (.Tags[]?.Key  == "createdBy" )) |  select(.AutoScalingGroupName != null) | {"ASG": .AutoScalingGroupName, "awsRegion": (.ARN | split(":") | .[3]), "Account": (.ARN | split(":") | .[4])}] | group_by(.Account)|  .[1][] | @sh "AWS_PROFILE=example-profile aws autoscaling delete-auto-scaling-group --auto-scaling-group-name \(.ASG) --region \(.awsRegion)" ' aws-asg.json
```

```
jq -r  '[.[] | del(select (.Tags[]?.Key  == "createdBy" )) | select(.StackId != null) | {"StackId": .StackId, "StackName": .StackName, "awsRegion": (.StackId | split(":") | .[3]), "Account": (.StackId | split(":") | .[4]), "StackStatus": .StackStatus}] | group_by(.Account) | .[1][] | if .StackStatus == "DELETE_FAILED" then @sh "AWS_PROFILE=example-profile aws --region \(.awsRegion) cloudformation delete-stack --stack-name \(.StackName) " else empty end'  aws-cf.json
```


[garnaat]: https://github.com/scopely-devops/skew#more-examples
[JQ]: https://stedolan.github.io/jq/
[Scopely]: http://scopely.com/
[skew]: https://github.com/scopely-devops/skew
