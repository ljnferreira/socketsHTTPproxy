#-------------------------------------------------
#   proxy_web.py
#
#   Servidor proxy HTTP Web multithreaded
#
#   Autores: 
#   Gabriel Lavarini <lavarinimoreira@gmail.com>
#   João Lucas Terra <jlterrafarias@gmail.com>
#   Lucas Ferreira <ljnferreira@gmail.com>
#
#-------------------------------------------------

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
        print("[*] Inicializando Socket...")
        print("[*] Pronto.")
        print("[*] Socket vinculado com sucesso...")
        print("[*] Servidor inicializado com sucesso ouvindo na porta[{}]".format(PORTA))
    except Exception as e:
        print(e)
        sys.exit(2)

    while True:
        try:
            conn,addr = s.accept()
            data = conn.recv(TAMANHO_BUFFER)
            _thread.start_new_thread(connection,(conn, data, addr))
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Desligando servidor de forma graciosa")
            print("[*] Aguardando requisições encerrarem...")
            print("[*] Pronto, foi um prazer te-lo como usuario do nosso serviço!")
            sys.exit(1)

def connection(conn, data, addr):
    try: 
        print(addr)
        # Obtém o conteúdo da primeira linha da requisição do cliente e exibe no log.
        first_line = data.decode('latin-1').split("\n")[0] 
        print(first_line)
        
        # Obtém a url e a posição da última barra relativa a definição do protocolo na url para obter o endereço de destino.
        url = first_line.split(" ")[1]
        http_pos = url.find("://")

        if http_pos == -1:
            pureURL = url
        else:
            pureURL = url[(http_pos + 3):]
            
        port_pos = pureURL.find(":")
        address_pos = pureURL.find("/")
        if address_pos == -1:
            address_pos = len(pureURL)

        server_address = ""
        port = -1

        # Verifica se a url contém o número da porta, caso não contenha, define o mesmo como 80.
        if port_pos == -1 or address_pos < port_pos:
            port = 80
            server_address = pureURL[:address_pos]
        else:
            port = int(pureURL[(port_pos + 1):][:address_pos - port_pos -1])
            server_address = pureURL[:port_pos]

        print(server_address)
        proxy_server(server_address,port,conn,data,addr)
    except Exception as e:
        print(e)
        traceback.print_exc()
        
def proxy_server(webserver, port, conn, data, addr):
    print("{} {} {} {}".format(webserver, port, conn, addr))
    try:
        print("\n\n[*] Abrindo conexão com o servidor ...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        print("\n\n[*] Enviando requisição...")
        s.send(data)
        while 1:
            print("\n\n[*] Recebendo Dados...")
            reply = s.recv(TAMANHO_BUFFER)
            
            if len(reply) > 0:
                conn.sendall(reply)
                print("[*] Requisição enviada: {} > {}".format(addr[0],webserver))
            else:
                print("\n\n[*] Dados obtidos com sucesso...")
                break        
        
        s.close()
        conn.close()
        print("\n\n[*] Conexões encerradas...")
        
    #Caso dispare alguma exceção durante a execução da thread, a exceção é mostrada no log e as conexões são fechadas e a thread é encerrada
    except Exception as e:
        print(e)
        traceback.print_exc()
        s.close()
        conn.close()
        sys.exit(1)

if __name__ == "__main__":
    main()