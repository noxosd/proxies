import socket, sys, struct, select, time, os

class SocksServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect_to_target(self, sock, target_ip, target_port):
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(0)
        target.connect((target_ip, target_port))
        self.__serve_connections([target, sock])
        target.close()

    def parse_greeting(self, data):
        params = struct.unpack("ccHIs", data)
        print "SOCKS version: %d" % (ord(params[0]),)
        print "Command code: %d" % (ord(params[1]),)
        print "Port number: %d" % (socket.ntohs(params[2]),)
        print "IP: %s" % ((socket.inet_ntoa(struct.pack("<L",params[3]))),)    

    def start(self):
        ack = struct.pack("ccHI",chr(0), chr(90),1,1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        while True:
            connection, address = self.sock.accept()
            print "Connection accepted from %s %s" % address
            pid = os.fork()
            print "Succesfully forked!"
            if pid == 0:
                while True:            
                    print "Child %d working" % (os.getpid())
                    print "Client (%s, %s) connected" % address
                    data = self.__recv_timeout(connection)
                    params = struct.unpack("ccHIs", data)
                    if ord(params[0])!=4 and ord(params[1])!=1:
                        sys.exit(1)
                    target_port = socket.ntohs(params[2])
                    target_ip = socket.inet_ntoa(struct.pack("<L", params[3]))
                    print target_port
                    print target_ip
                    connection.sendall(ack)
                    self.connect_to_target(connection, target_ip, target_port)
                    connection.close()            
                    print "Connection closed"
                    sys.exit(1)
            else:
                print
                 
    def __serve_connections(self, sockets):
        while True:
            input, output, error = select.select(sockets, sockets, [])
            for i in input:
                if i == sockets[0]:
                   if self.__recv_and_send(i, sockets[1]) == "": return
                else:
                    if self.__recv_and_send(i, sockets[0]) == "": return
     
    def __recv_and_send(self, receiver, sender):
        data = self.__recv_timeout(receiver)                
#        print data
        sender.sendall(data)
        return data

    def __recv_timeout(self, the_socket, timeout=1):
        the_socket.setblocking(0)
        total_data = []
        data = []
        begin = time.time()
        while True:
            if total_data and time.time() - begin > timeout:
                break
            elif time.time()-begin > timeout*2:
                break
            try:
                data = the_socket.recv(8192)
                if data:
                    total_data.append(data)
                    begin = time.time()
                time.sleep(0.1)
            except:
                pass
        return "".join(total_data)

def main():
    serv = SocksServer("127.0.0.1", 8080)
    while True:
        try:
            serv.start()
            time.sleep(5)
        except KeyboardInterrupt:
            sys.exit(1)
        except OSError:
            print "OSError"
       
if __name__=="__main__":
    main()
