"""Instrument server.
Used to save python data and echo it.
Server is implemented in TwistedMatrix - Takes advantage of 
a good architecture. All is based on the reactor paradigm, a single main
loop.

Client is implemented via Python socket - bare bone, but doesnt require
asyncronous paradigm.

To use it
Executing the script starts a server on port 9999

from instserver import Connection

# Create connection
c = Connection('localhost',9999)
# write values
c.values([1,2,3,4])
# read values
print c.read()
"""

# create a JSON-RPC-server
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
server = SimpleJSONRPCServer(('localhost', 9999))

server.values = [42,1984]

def values(val = None):
    if val:
        server.values = val
    return server.values
                        
# start server
server.register_function(values)
server.serve_forever()        