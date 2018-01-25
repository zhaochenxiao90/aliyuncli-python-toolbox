#!/usr/bin/env python
import json,sys,os,argparse,subprocess,csv,re
from subprocess import call
from time import sleep
from pprint import pprint
from urlparse import urlparse

parser = argparse.ArgumentParser(description="""
High level script that invalidates the cache in bulk using a CSV or JSON file.

Examples:
    acs/cdn/bulk_invalidate.py --file acs/cdn/bulk_invalidate_sample.csv 
    acs/cdn/bulk_invalidate.py --file acs/cdn/bulk_invalidate_sample.json --format json
""",formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument(
    '--file', metavar="FILE", type=str, dest='file', required=True,
    action='store', help='File containing urls of files and directories to invalidate. Note that directories must end with a "/"')
parser.add_argument(
    '--format', metavar='FORMAT', type=str, dest='format', default='csv',
    help='A value of "csv" or "json". Default is "csv"')
args = parser.parse_args()

file=args.file
format=args.format
cli = 'aliyuncli'

if format not in ["csv", "json"]:
    print 'Failed: format must be "csv" or "json"'
    exit(1)

try:
   proc = subprocess.call("{cli}".format(**locals()), stdout=subprocess.PIPE)
except:
   print "Failed: aliyuncli could not be found; please ensure it is installed and executable by current user; aborting..."
   exit(1)

data = {"files": [], "dirs": []}
try:
    with open(file, 'rb') as raw:
        if format == "csv":
            input = csv.reader(raw, delimiter=' ', quotechar='|')
            for row in input:
                if (len(row)) != 1:
                    print "Failed: row {row}, value  has more than 1 item".format(**locals())
                    exit(1)
                result = urlparse(row[0])
                if result.scheme and result.netloc and result.path:
                    if row[0].endswith('/'):
                        data["dirs"].append(row[0])
                    else:
                        data["files"].append(row[0])
                    continue
                print "Failed: row {row} is not a valid url".format(**locals())
                exit(1)
        if format == "json":
            input = json.load(raw)
            for row in input:
                cond0 = (type(row) == str or type(row) == unicode)
                cond1 = 'url' in row
                if cond0 == True or cond1 == True:
                    u = row
                    if cond0:
                        result = urlparse(row)
                    else:
                        u = row['url']
                        result = urlparse(row['url'])
                    if result.scheme and result.netloc and result.path:
                        if u.endswith('/'):
                            data["dirs"].append(u)
                        else:
                            data["files"].append(u)
                        continue
                print "Failed: row {row} must be a string url or an object like {{\"url\":\"http://sample\"}}".format(**locals())
                exit(1)
except Exception as e:
    print "Failed: Could not open file {file}".format(**locals())
    print "Details:"
    print e
    exit(1)

if len(data) == 0:
    print 'No items to invalidate'
    exit(0)

print "Invalidating files:".format(**locals())
try:
    path = " ".join(data["files"])
    obj = subprocess.check_output("{cli} cdn RefreshObjectCaches --ObjectType File --ObjectPath {path}".format(**locals()), shell=True)
    print obj
except Exception as e:
    print "Failed to invalidate files"
    print e

print "Invalidating dirs:".format(**locals())
try:
    path = " ".join(data["dirs"])
    obj = subprocess.check_output("{cli} cdn RefreshObjectCaches --ObjectType Directory --ObjectPath {path}".format(**locals()), shell=True)
    print obj
except Exception as e:
    print "Failed to invalidate files"
    print e