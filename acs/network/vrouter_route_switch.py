#!/usr/bin/env python
import json,sys,os,argparse,subprocess;
from subprocess import call;
from time import sleep;

parser = argparse.ArgumentParser(description='Switches route entries from HAVIP, Instance or RouterInterface and vice versa.')
parser.add_argument('--vrouter_id', metavar="ID", type=str, dest='vrouter_id', action='store', help='VRouterId to which the routing table is bound to.', required=True)
parser.add_argument('--cidr', metavar="CIDR_BLOCK", dest='cidr', action='store', help='CIDR block that identifies the route.', required=True )
parser.add_argument('--havip', metavar="HAVIP_ID", type=str, dest='havip', action='store', help='HAVIP to switch over to/from.')
parser.add_argument('--inst', metavar="INSTANCE_ID", type=str, dest='inst', action='store', help='Instance id to switch over to/from.')
parser.add_argument('--router_interface', type=str, metavar="ROUTER_INTERFACE_ID", dest='router', action='store', help='Router interface id to switch over to/from.')
parser.add_argument('--sleep', metavar='N', type=int, dest='sl', default=20, help='Seconds to wait between API calls for modifying routes.')
args = parser.parse_args()

vrouter_id=args.vrouter_id
cidr=args.cidr
inst=(args.inst if args.inst else '')
havip=(args.havip if args.havip else '')
router=(args.router if args.router else '')
sl = float(args.sl)
cli = 'aliyuncli'

check = (1 if len(inst) > 0 else 0) + (1 if len(havip) > 0 else 0) + (1 if len(router) > 0 else 0)
if check != 2:
   print "Wrong combination of options: any 2 of [havip, inst, router_interface] must be specified."
   exit(1)

try:
   proc = subprocess.call("{cli}".format(**locals()), stdout=subprocess.PIPE)
except:
   print "aliyuncli could not be found; please ensure it is installed and executable by current user; aborting..."
   exit(1)

obj = subprocess.check_output("{cli} ecs DescribeRouteTables --VRouterId {vrouter_id}".format(**locals()), shell=True)
obj=json.loads(obj);

routes=obj['RouteTables']['RouteTable'][0]['RouteEntrys']['RouteEntry'];
route_table_id = type = id = None
for r in routes:
    if r['DestinationCidrBlock'] == cidr:
       route_table_id = r['RouteTableId']
       type = r['NextHopType']
       id = r['InstanceId']
       break;

if type == None or id == None:
   print "No such route found: {vrouter_id} {cidr}".format(**locals())
   exit(1)

target_type = target_inst = ''
for k,v in {'Instance': inst, 'HaVip':havip, 'RouterInterface':router}.items():
   if len(v) > 0 and v != id:
       target_type = k
       target_id = v
       continue

print "{id} ({type}) -> {target_id} ({target_type})".format(**locals()) 
os.system("{cli} ecs DeleteRouteEntry --RouteTableId {route_table_id} --DestinationCidrBlock {cidr} --NextHopId {id}".format(**locals()))
sleep(sl)
os.system("{cli} ecs CreateRouteEntry --RouteTableId {route_table_id} --DestinationCidrBlock {cidr} --NextHopType {target_type} --NextHopId {target_id}".format(**locals()))
sleep(sl)
print 'Done'