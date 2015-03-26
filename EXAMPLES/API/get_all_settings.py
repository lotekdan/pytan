
"""
Get all system settings
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
PORT = "444"

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
kwargs["objtype"] = u'setting'

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
Handler for Session to 172.16.31.128:444, Authenticated: True, Version: 6.2.314.3279

Type of response:  <class 'taniumpy.object_types.system_settings_list.SystemSettingsList'>

print of response:
SystemSettingsList, len: 88

length of response (number of objects returned): 
88

print the first object returned in JSON format:
{
  "_type": "system_setting", 
  "audit_data": {
    "_type": "audit_data", 
    "creation_time": "2015-03-03T19:06:08", 
    "last_modified_by": "Jim Olsen", 
    "modification_time": "2015-03-03T19:06:08"
  }, 
  "cache_row_id": 0, 
  "default_value": "0", 
  "hidden_flag": 0, 
  "id": 1, 
  "name": "load_initial_content", 
  "read_only_flag": 0, 
  "setting_type": "Server", 
..trimmed for brevity..

'''