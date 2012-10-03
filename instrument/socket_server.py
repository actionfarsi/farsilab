import threading, SocketServer, pickle, time, numpy
import socket
import pickle, time, json


class TCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        data = json.loads(self.rfile.readline())
                
        # Check is present in dictionary
        response = self.server.binder[data['method']](data['params'])
        self.request.send(json.dumps({      "jsonrpc": "2.0",
                                            'response': response,
                                            'id': data['id']  }))
                    
            
def server(commands= {'log': 0}):
    HOST, PORT = "", 9999
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), TCPHandler)
    
    def values(values = None):
        if values is not None:
            server.values = values
        return server.values
    
    server.binder = {'values': values }
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    
    server.log = ""
    server.values = []
    
    return server

def connect(command, host, port = 9999):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(command)
    data = s.recv(2**15)
    
    return data
    s.close()
    
    
if __name__ == '__main__':
    s = server()
    i = 0
    while True:
        i = i +1
        time.sleep(0.5)
        s.values = [i%20, i%20+1]
        