
"""
Get all sensors
"""

import os
import sys
sys.dont_write_bytecode = True

# Determine our script name, script dir
my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)

# determine the pytan lib dir and add it to the path
parent_dir = os.path.dirname(my_dir)
pytan_root_dir = os.path.dirname(parent_dir)
lib_dir = os.path.join(pytan_root_dir, 'lib')
path_adds = [lib_dir]

for aa in path_adds:
    if aa not in sys.path:
        sys.path.append(aa)


# connection info for Tanium Server
USERNAME = "Tanium User"
PASSWORD = "T@n!um"
HOST = "172.16.31.128"
PORT = "443"

# Logging conrols
LOGLEVEL = 2
DEBUGFORMAT = False

import tempfile

import pytan
handler = pytan.Handler(
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    loglevel=LOGLEVEL,
    debugformat=DEBUGFORMAT,
)

print handler

# setup the arguments for the handler method
kwargs = {}
kwargs["objtype"] = u'sensor'

# call the handler with the get_all method, passing in kwargs for arguments
response = handler.get_all(**kwargs)

print ""
print "Type of response: ", type(response)

print ""
print "print of response:"
print response

print ""
print "length of response (number of objects returned): "
print len(response)

print ""
print "print the first object returned in JSON format:"
out = response.to_json(response[0])
if len(out.splitlines()) > 15:
    out = out.splitlines()[0:15]
    out.append('..trimmed for brevity..')
    out = '\n'.join(out)

print out



'''Output from running this:
Handler for Session to 172.16.31.128:443, Authenticated: True, Version: Not yet determined!

Type of response:  <class 'taniumpy.object_types.sensor_list.SensorList'>

print of response:
SensorList, len: 419

length of response (number of objects returned): 
419

print the first object returned in JSON format:
{
  "_type": "sensor", 
  "cache_row_id": 0, 
  "category": "Reserved", 
  "description": "The recorded state of each action a client has taken recently in the form of id:status.\nExample: 1:Completed", 
  "exclude_from_parse_flag": 1, 
  "hash": 1792443391, 
  "hidden_flag": 0, 
  "id": 1, 
  "ignore_case_flag": 1, 
  "max_age_seconds": 3600, 
  "name": "Action Statuses", 
  "queries": {
    "_type": "queries", 
    "query": [
..trimmed for brevity..

'''
