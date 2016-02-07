import socket, sys, struct, select, time, os

class SocksServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect_to_target(self, target_ip, target_port):
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect((target_ip, target_port))
        if target is None:
            print "Socket cannot connect"
        print "Connected to %s %d" % (target_ip, target_port)
        return target

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
        sock_list = [self.sock]
        client_connection = {}
        while True:
            readable, writable, error_sockets = select.select(sock_list, [], [])
            for r in readable:
                if r == self.sock:
                    connection, address = self.sock.accept()
                    print "Client (%s, %s) connected" % address
                    sock_list.append(connection)
                    data = self.__recv_timeout(connection)
                    params = struct.unpack("ccHIs", data)
                    if ord(params[0])!=4 and ord(params[1])!=1:
                            sys.exit(1)
                    target_port = socket.ntohs(params[2])
                    target_ip = socket.inet_ntoa(struct.pack("<L", params[3]))
                    print "Client %s wants to connect to %s:%d" % (address, target_ip, target_port)
                    client_connection[connection] = [self.connect_to_target(target_ip, target_port), 3]
                    connection.sendall(ack)
                elif r in client_connection.keys():
                    print "Client connection proceed"
                    if client_connection[r] is not None and r is not None:
                        try:
                            flag = self.__serve_connections([r, client_connection[r][0]])
                            if not flag:
                                client_connection[r][1] -= 1
                            if client_connection[r][1] == 0:
                                client_connection[r][0].close()
                                del client_connection[r]
                                sock_list.remove(r)
                                r.close()
                                print "Connection closed"
                        except socket.error:
                            print "Broken pipe\r\nConnection closed"
                        
                 
    def __serve_connections(self, sockets, timeout=3):
        begin = time.time()
        while True:
            print "Serving connection..."
            readable, writable, errorable = select.select(sockets, [], [], 1)
            for r in readable:
                if r == sockets[0]:
                    data = self.__recv_and_send(sockets[0], sockets[1])
                    if data != "":
                        begin = time.time()
                else:
                    data = self.__recv_and_send(sockets[1], sockets[0])
                    if data != "":
                        begin = time.time()
            if data == "":
                print "No data. Socket possible closed"
                return False
            if time.time()-begin > timeout*1.5:
                print "Timer"
                return False
            print "New timer!"
            begin = time.time()
            timeout -= 0.5
            if timeout == 0:
                return False

    def __recv_and_send(self, receiver, sender):
        data = self.__recv_timeout(receiver)                
        print "============================================"
        print data
        print "============================================"
        sender.sendall(data)
        return data

    def __recv_timeout(self, the_socket, timeout=1):
        print "Receiving data"
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
        the_socket.setblocking(1)
        return "".join(total_data)

def main():
    serv = SocksServer("127.0.0.1", 8080)
    while True:
        try:
            serv.start()
        except OSError:
            print "OSError"
       
if __name__=="__main__":
    main()
