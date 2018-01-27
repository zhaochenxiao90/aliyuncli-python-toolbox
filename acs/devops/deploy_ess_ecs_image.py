#!/usr/bin/env python
import json,sys,os,argparse,subprocess
from subprocess import call
from time import sleep

parser = argparse.ArgumentParser(description="""
Script to do deploy applications behind an SLB with no downtime using ESS and ECS Images.
It requires that an ESS group is set up beforehand.

Flow:
1. Create/use ECS image
2. Create a new Scaling Configuration
3. Modify the Scaling Group to use new Scaling Configuration
4. Upsize the Scaling Group by 2
5. Wait
6. Halve the Scaling group
7. Remove old Scaling Configurations

Examples:
1. Create an image then use that image to spawn:
./deploy_ess_ecs_image.py --inst i-t4n82afwqqn07r6y05u4 --ess-seed asc-t4nenmrgzio42w6ym5pv

2. Use an existing image:
./deploy_ess_ecs_image.py --image m-t4n7fgdttcf8l65dv8b7 --ess-seed asc-t4nenmrgzio42w6ym5pv
""",formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('--inst', metavar="INSTANCE_ID", type=str, dest='inst', action='store', help='Instance ID to create Image from')
parser.add_argument('--image', metavar="IMAGE_ID", type=str, dest='image', action='store', help='Image ID to use (overrides "--inst" param)')
parser.add_argument('--ess-seed', metavar="ESS_CLONE", type=str, dest='ess_seed', required=True,  action='store', help='ESS Configuration to copy settings over from.')
parser.add_argument('--sleep', metavar='SLEEP', type=int, dest='sl', default=5, help='Seconds to wait between API calls.')
parser.add_argument('--wait', metavar='WAIT', type=int, dest='wait', help='If specified, will wait this number of seconds before halving the Scaling Group.')
args = parser.parse_args()

inst=(args.inst if args.inst else '')
image=(args.image if args.image else '')
ess_seed = args.ess_seed
sl = float(args.sl)
wait = (float(args.wait) if args.wait else None)

cli = 'aliyuncli'

try:
   proc = subprocess.call("{cli}".format(**locals()), stdout=subprocess.PIPE)
except:
   print "aliyuncli could not be found; please ensure it is installed and executable by current user; aborting..."
   exit(1)

if not inst and not image:
   print 'Failed: "inst" or "image" must be specified'
   exit(1)

if image:
    print "Using image {image}".format(**locals())
else:
    print "Creating image from instance {inst}".format(**locals())
    obj = subprocess.check_output("{cli} ecs CreateImage --InstanceId {inst}".format(**locals()), shell=True)
    print obj
    obj = json.loads(obj)
    image=obj['ImageId']

# wait/check image is ready
print "Checking for image {image} readiness ...".format(**locals())
while True:
    try:
        obj = subprocess.check_output("{cli} ecs DescribeImages --ImageId {image}".format(**locals()), shell=True)
        obj = json.loads(obj)
        if obj['Images']['Image']:
            p = obj['Images']['Image'][0]['Progress']
            print "{image} is at {p}".format(**locals())
            if p == '100%':
                break
        else:
            print "{image} not ready".format(**locals())
            sleep(sl)
    except Exception as e:
        print e
        exit(1)

try:
    print "Reading params from Scaling Configuration ..."
    obj = subprocess.check_output("{cli} ess DescribeScalingConfigurations --ScalingConfigurationId1 {ess_seed}".format(**locals()), shell=True)
    tpl = json.loads(obj)['ScalingConfigurations']['ScalingConfiguration'][0]
    disks = ''
    i = 1
    for d in tpl['DataDisks']['DataDisk']:
        disks = disks + "--DataDisk{i}Category {d[Category]} --DataDisk{i}Size {d[Size]}".format(**locals())
        i = i + 1
    sg = tpl['ScalingGroupId']

    print "Reading min and max from Scaling Group ..."
    obj = subprocess.check_output("{cli} ess DescribeScalingGroups --ScalingGroupId1 {sg}".format(**locals()), shell=True)
    obj = json.loads(obj)
    min = obj['ScalingGroups']['ScalingGroup'][0]['MinSize']
    max = obj['ScalingGroups']['ScalingGroup'][0]['MaxSize']
    min2 = min * 2
    max2 = max * 2

    print "Creating Scaling Configuration..."
    obj = subprocess.check_output(
        "{cli} ess CreateScalingConfiguration \
            --SystemDiskCategory {tpl[SystemDiskCategory]} \
            --SystemDiskSize {tpl[SystemDiskSize]} \
            --InternetChargeType {tpl[InternetChargeType]} \
            --InternetMaxBandwidthOut {tpl[InternetMaxBandwidthOut]} \
            --ScalingGroupId {sg} \
            --ImageId {image} \
            {disks} \
            --SecurityGroupId {tpl[SecurityGroupId]} \
            --InstanceType {tpl[InstanceType]}"
            .format(**locals()), shell=True)
    print obj
    obj = json.loads(obj)
    sc_id = obj['ScalingConfigurationId']

    print "Updating Scaling Group: scaling config:{sc_id}, min: {min2}, max: {max2} ...".format(**locals())
    obj = subprocess.check_output(
        "{cli} ess ModifyScalingGroup --ScalingGroupId {sg} --ActiveScalingConfigurationId {sc_id} --MinSize {min2} --MaxSize {max2}"
            .format(**locals()), shell=True)
    print obj

    if wait:
        print "Sleeping {wait} seconds ..."
        sleep(wait)
    else:
        loop = True
        while loop:
            print "Checking for running instances with new config ..."
            obj = subprocess.check_output("{cli} ess DescribeScalingInstances --ScalingGroupId {sg} --ScalingConfigurationId {sc_id}".format(**locals()), shell=True)
            obj = json.loads(obj)['ScalingInstances']['ScalingInstance']
            for o in obj:
                if o['ScalingConfigurationId'] == sc_id and o['LifecycleState'] == 'InService' and o['HealthStatus'] == 'Healthy':
                    print "Healthy instance {o[InstanceId]} found with new configuration.".format(**locals())
                    loop = False
                    break
            sleep(sl)

    print "Halving Scaling Group: scaling config:{sc_id}, min: {min}, max: {max} ...".format(**locals())
    obj = subprocess.check_output("{cli} ess ModifyScalingGroup --ScalingGroupId {sg} --MinSize {min} --MaxSize {max}".format(**locals()), shell=True)
    print obj
except Exception as e:
    print e
    exit(1)