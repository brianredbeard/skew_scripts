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


arn = scan('arn:aws:autoscaling:*:*:autoScalingGroup:*')

asgs = []

for resource in arn:
    resource.data['ARN'] = resource.arn
    asgs.append(resource.data)

with open('aws-asg.json', mode='w') as f:
    json.dump(asgs, f, default=json_serial, indent=2)
