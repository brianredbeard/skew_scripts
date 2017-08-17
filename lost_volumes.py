import json
import skew

from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")



total_size = 0
total_volumes = 0

volumes = []
for volume in skew.scan('arn:aws:ec2:*:*:volume/*'):
    if not volume.data['Attachments']:
        total_volumes += 1
        total_size += volume.data['Size']
        print('%s: %dGB' % (volume.arn, volume.data['Size']))
        volume.data['ARN'] = volume.arn
        print('  - Created: %s' % volume.data['CreateTime'])
        if volume.data['SnapshotId'] != '':
            print('  - Snapshot: %s' % volume.data['SnapshotId'])
        volumes.append(volume.data)

print('Total unattached volumes: %d' % total_volumes)
print('Total size (GB): %d' % total_size)

#print(json.dumps(volumes, default=json_serial, indent=2))
