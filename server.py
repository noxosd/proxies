import socket, sys, select

def serve(conn, relay_server):
    relay_conn, relay_address = relay_server.accept()
    socket_list = [conn, relay_conn]
    while True:
        input, output, error = select.select(socket_list, socket_list, [])
        for i in input:
            if i == conn:
                data_conn = conn.recv(4096)
                relay_conn.send(data_conn)
            else: 
                data_relay = relay_conn.recv(4096)
                if data_relay == "":
                    print "Client disconnected..."
                    return
                conn.send(data_relay)

def main():
    HOST = "127.0.0.1"
    port = 53
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    relay_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    relay_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    relay_server.bind((HOST, 8080))
    server.listen(5)
    conn, address = server.accept()
    relay_server.listen(5)
    data_conn = ""
    data_relay = ""
    while True:
        serve(conn, relay_server)

if __name__ == "__main__":
   try:
        main()
   except KeyboardInterrupt:
        print "User exit"
        sys.exit(1)
