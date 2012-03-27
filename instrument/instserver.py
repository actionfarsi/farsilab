import threading, SocketServer, pickle, time, numpy
import socket

class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # Check is present in dictionary
        if self.data == "log":
            self.request.send(self.server.log)
            return
        if self.data == "monitor":
            self.request.send(pickle.dumps(self.server.values))
            
        try:
            self.response = self.server.commands[self.data]()
            self.request.send(self.response)
        except:
            self.request.send(self.server.log)

def server(commands= {'log': 0}):
    HOST, PORT = "", 9999
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), TCPHandler)
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
        time.sleep(0.3)
        s.values = [numpy.linspace(i,i+2,3),numpy.linspace(i-5,i+2-5,3),]
        