#!/usr/bin/python

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


arn = scan('arn:aws:ec2:*:*:snapshot/*')

count = 0
snapshots = []

count = 0
print("Retreiving instance information...")
for resource in arn:
    count+=1
    if count % 100 == 0:
        print("Processed {} entries".format(count))
    resource.data['ARN'] = resource.arn
    snapshots.append(resource.data)

with open('aws-snapshots.json', mode='w') as f:
    json.dump(snapshots, f, default=json_serial, indent=2)
