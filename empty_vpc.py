#!/usr/bin/python
from __future__ import print_function
import argparse
import json
import os
import skew
import sys
import tempfile
from datetime import datetime
from pprint import pprint


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


def getVPCs(account="*", region="*", debug=False, save=False):
    """Retrieve all data on VPCs from an AWS account and optionally save
    data on each to a file"""

    print("Collecting VPC data...", file=sys.stderr)
    vpclist = {}
    for vpc in skew.scan("arn:aws:ec2:%s:%s:vpc/*" % (region, account)):
        if debug:
            msg = "Account: %s, VPCID: %s, Region: %s, CIDR: %s" % ( 
            vpc._client.account_id, vpc.id, vpc._client.region_name, 
                    vpc.data['CidrBlock'])
            print(msg, file=sys.stderr)
        try:
            tags = vpc.data['Tags']
        except KeyError:
            tags = []

        vpclist[vpc.id] = {"CIDR": vpc.data['CidrBlock'],
                            "Account": vpc._client.account_id,
                            "Region": vpc._client.region_name,
                            "Tags": tags,
                            "Instances":[]}

    vpclist['none'] = {"Instances":[]}
    print("Collected information on %s VPCs" % len(vpclist), file=sys.stderr)
    return vpclist

def getInstances(vpclist, account="*", region="*", debug=False):
    """Given a dictionary of VPCs, populate it with the list of instances"""
    print("Collecting EC2 instance data...", file=sys.stderr)
    count = 0
    for instance in skew.scan("arn:aws:ec2:%s:%s:instance/*" % (region, account)):
        count += 1
        try:
            if debug:
                print(instance.data['VpcId'], file=sys.stderr)
            vpclist[instance.data['VpcId']]['Instances'].append(instance.id)
            vpclist[instance.data['VpcId']]['Instances'].append(
                    {instance.id: instance.data})
        except KeyError:
            if debug:
                print("Orphan Instance,ACC,", instance._client.account_id, 
                    ",ID,",instance.id, file=sys.stderr)
            vpclist['none']['Instances'].append({instance.id: instance.data})
    print("Collected information on %s EC2 instances" % count, file=sys.stderr)
    return vpclist

def saveJSON(data, fname='empty_vpc.json'):
    """Serialize a python data structure to a JSON file"""
    try:
        with open(fname, mode='w') as f:
            json.dump(data, f, default=json_serial, indent=2)
        f.close()
    except:
        print("Could not write to file %s" % fname, file=sys.stderr)
        print(sys.exc_info()[0], file=sys.stderr)

def loadJSON(fname='empty_vpc.json'):
    """Deserialize a python data structure from a JSON file"""
    try:
        with open(fname, mode='r') as f:
            data = json.load(f)
        f.close()
        return data
    except:
        print("Could not read from file %s" % fname, file=sys.stderr)

def main():
    option_parser = argparse.ArgumentParser()
    option_parser.add_argument('--region', '-r', type=str, dest='region', 
            default='*', help='AWS Region (default: %(default)s)')
    option_parser.add_argument('--account', '-a', type=str, dest='account', 
            default='*', help='AWS Account (default: %(default)s)')
    option_parser.add_argument('--blast', '-b', dest='blast',
            action="store_true", 
            help='Write files for each vpc into a temp dir (/tmp/vpc-XXXXXX)')
    option_parser.add_argument('--save', '-s', dest='sfile', 
            default="", help='Save retrieved data to a file')
    option_parser.add_argument('--load', '-l', dest='lfile', default="",
            help='Load data from file (make no network calls)')
    option_parser.add_argument('--debug', '-d', dest='debug', 
            action="store_true",
            help='Load data from file (make no network calls)')
    args = option_parser.parse_args()

    if args.account == "*":
        acc = "all_accounts"
    else:
        acc = args.account

    if args.region == "*":
        reg = "all_regions"
    else:
        reg = args.region

    if len(args.lfile) > 0:
        vlist = loadJSON(fname=args.lfile)
    else:
        vlist = getVPCs(account=args.account, region=args.region,
                debug=args.debug, save=args.blast)
        vlist = getInstances(vlist, account=args.account, region=args.region,
                debug=args.debug)

        if len(args.sfile) > 0:
            if args.debug:
                print("Attempting save to file %s" % args.sfile, 
                        file=sys.stderr)
            saveJSON(vlist, fname=args.sfile)

    if args.blast:
        tempdir = tempfile.mkdtemp("","empty-vpc-")
        print("Saving all VPC data to %s" % tempdir)
    print("Account,VPCID")
    for k,v in vlist.iteritems():
        try:
            account = v['Account']
            region = v['Region']
        except KeyError as e:
            print("Missing key --", e)
            account = ""
            region = ""

        if args.debug:
            print("%s - %s" % (k, v), file=sys.stderr)
        if args.blast:
            filepath=os.path.join(tempdir,account,region,k)
            os.makedirs(filepath,0700)
            
            vpcfile = os.path.join(filepath,"%s.json" % k)
            saveJSON({k:v}, fname=vpcfile)
        l = len(v['Instances'])
        if l < 1:
            print("%s,%s" % (v['Account'], k))


if __name__ == '__main__':
    main()
