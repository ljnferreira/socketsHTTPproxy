import socket,sys,_thread,traceback

 
PORTA = 8080
TAMANHO_BUFFER = 10000
MAXIMO_CONEXOES = 10000

def main():
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", PORTA))
        s.listen(MAXIMO_CONEXOES)
        print("[*] Intializing socket. Done.")
        print("[*] Socket binded successfully...")
        print("[*] Server started successfully [{}]".format(PORTA))
    except Exception as e:
        print(e)
        sys.exit(2)

    while True:
        try:
            conn,addr = s.accept()
            data = conn.recv(TAMANHO_BUFFER)
            _thread.start_new_thread(conn_string,(conn, data, addr))
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Shutting down...")
            sys.exit(1)

def conn_string(conn, data, addr):
    try: 
        print(addr)
        first_line = data.decode('latin-1').split("\n")[0]
        print(first_line)
        url = first_line.split(" ")[1]
        
        http_pos = url.find("://")
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]
            
        port_pos = temp.find(":")
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int(temp[(port_pos + 1):][:webserver_pos - port_pos -1])
            webserver = temp[:port_pos]

        print(webserver)
        proxy_server(webserver,port,conn,data,addr)
    except Exception as e:
        print(e)
        traceback.print_exc()
        
def proxy_server(webserver, port, conn, data, addr):
    print("{} {} {} {}".format(webserver, port, conn, addr))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(data)
        while 1:
            reply = s.recv(TAMANHO_BUFFER)
            
            if len(reply) > 0:
                conn.sendall(reply)
                print("[*] Request sent: {} > {}".format(addr[0],webserver))
            else:
                break        
        
        s.close()
        conn.close()
        
    except Exception as e:
        print(e)
        traceback.print_exc()
        s.close()
        conn.close()
        sys.exit(1)

if __name__ == "__main__":
    main()