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

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, defer

import threading, socket

import pickle, time, json

class Instrument(LineReceiver):
    def __init__(self,server):
        print "Starting connection"
        self.server = server
        self.state = 'SEND'
    
    def lineReceived(self, line):
        command = json.loads(line)
        d = defer.Deferred()
        d.addCallback(self.findMethod,command)
        #d.addCallback(self._method, self._params)
        d.addCallback(self.respond)
        reactor.callWhenRunning (d.callback, 0)
    
    def findMethod(self,command):
        self._method = handle_error
        if self.command['method'] == "values":
            self._method = self.server.f_values
            self._params = self.command['params']
            self._response = self._method(*self._params)
    
    def respond(self):
        response = json.dumps({  'response': self._response,
                                'id':0})
        self.sendLine(response)
    
    
    def handle_error(*arg):
        return "error"
    
    def handle_log(self):
        self.sendLine(server.log)
        
    def handle_monitor(self):
        self.sendLine(pickle.dumps(self.server.values))
        
    def handle_read(self,line):
        self.server.values = pickle.loads(line)
        

class Server(Factory):
    def __init__(self):
        self.log = ''
        self.values = [42,1984]

    def buildProtocol(self, add):
        return Instrument(self)
        
    def f_values(values = None):
        return self.values
        
# class InstrumentClient(protocol.Protocol):
    # def connectionMade(self):
        # self.factory.app.on_connection(self.transport)

    # def dataReceived(self, data):
        # self.factory.app.print_message(data)


# class ClientFactory(protocol.ClientFactory):
    # protocol = InstrumentClient
    
    # def __init__(self, address, port):
        # self.address = address
        # self.port = port

    # def buildProtocol(self, value):
        # return InstrumentClient()
        
    
    # def clientConnectionFailed(self, conn, reason):
        # print "connection failed"

    # def send_values(values):
        # reactor.connectTCP(self.address, self.port)
        
def startServer(commands= {'log': 0}):
    HOST, PORT = "", 9999
    server = Server()
    reactor.listenTCP(PORT, server)
    reactor.run()

class Connection:
    def __init__(self,host, port = 9999):
        self.termination = "\r\n"
        try:
            self.sock = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM)
            self.sock.connect((host, port))
            #self.sock.setblocking(0)
            
        except:
            print "Connection not established"
    
    def values(self,values):
        self.sock.send('give')
        self.sock.send(self.termination)
        self.sock.send(pickle.dumps(values))
        self.sock.send(self.termination)
    
    def read(self):
        self.sock.send('monitor')
        self.sock.send(self.termination)
        data = self.sock.recv(2**12)
        return pickle.loads(data)
    
    
    def close(self):
        self.sock.close()
    
def testConnection1():
    print "First conn"
    c = Connection('localhost',9999)
    c.values([1,2,3,4])
    print "Values sent"
    c.close()
    
def testConnection2():
    print "Second conn"
    c = Connection('localhost',9999)
    print c.read()
    print "Values got"
    c.close()
        
if __name__ == '__main__':
    startServer()
        