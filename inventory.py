#!/usr/bin/env python

import json
from datetime import datetime
from skew import scan
from pprint import pprint

from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


arn = scan('arn:aws:ec2:*:*:instance/*')

rds = scan('arn:aws:rds:*:*:db:*')
cf  = scan('arn:aws:cloudformation:*:*:stack/*')

count = 0
machines = []
databases = []
cfs = []

print("Retreiving cloud formation information...")
for resource in cf:
    count+=1
    if count % 10 == 0:
        print("Processed {} entries".format(count))
    #resource.data['ARN'] = resource.rds
    cfs.append(resource.data)

count = 0
print("Retreiving RDS information...")
for resource in rds:
    count+=1
    if count % 10 == 0:
        print("Processed {} entries".format(count))
    #resource.data['ARN'] = resource.rds
    databases.append(resource.data)

count = 0
print("Retreiving instance information...")
for resource in arn:
    count+=1
    if count % 10 == 0:
        print("Processed {} entries".format(count))
    resource.data['ARN'] = resource.arn
    machines.append(resource.data)

with open('aws-cf.json', mode='w') as f:
    json.dump(cfs, f, default=json_serial, indent=2)

with open('aws-rds.json', mode='w') as f:
    json.dump(databases, f, default=json_serial, indent=2)

with open('aws-ec2.json', mode='w') as f:
    json.dump(machines, f, default=json_serial, indent=2)
