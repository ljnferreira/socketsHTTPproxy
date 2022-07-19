#-------------------------------------------------
#   proxy_web.py
#
#   Servidor proxy HTTP Web multithreaded
#
#   Autores: 
#   Gabriel Lavarini <lavarinimoreira@gmail.com> <github.com/lavarinimoreira>
#   João Lucas Terra <jlterrafarias@gmail.com> <github.com/ja1za1>
#   Lucas Ferreira <ljnferreira@gmail.com> <github.com/ljnferreira>
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
        s.bind(("10.0.0.100", PORTA))
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
            
        # Essa exceção captura todas as exceções que não sejam interrupção de 
        # teclado para permitir que o programa continue rodando mesmo que seja 
        # disparada uma excessão, como ao não se ter mais memoria para criação
        # de nova thread.
        except Exception as e:
            print(e)
            traceback.print_exc()

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
            noProtocolURL = url
        else:
            noProtocolURL = url[(http_pos + 3):]

        #Verifica se há porta na url retornando a posição do caractere :    
        port_pos = noProtocolURL.find(":")

        # Procura a posição da primeira barra para determinar o fim do dominio
        address_pos = noProtocolURL.find("/")

        if address_pos == -1:
            address_pos = len(noProtocolURL)

        server_address = ""
        port = -1

        # Verifica se a url contém o número da porta, caso não contenha, define o mesmo como 80.
        if port_pos == -1 or address_pos < port_pos:
            port = 80
            server_address = noProtocolURL[:address_pos]
        else:
            port = int(noProtocolURL[(port_pos + 1):][:address_pos - port_pos -1])
            server_address = noProtocolURL[:port_pos]

        print(server_address)
        proxy_server(server_address,port,conn,data,addr)
    except Exception as e:
        print(e)
        traceback.print_exc()
        
def proxy_server(webserver, port, conn, data, addr):
    print("{} {} {} {}".format(webserver, port, conn, addr))
    try:
        print("\n[*] Abrindo conexão com o servidor ...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        print("\n[*] Enviando requisição...")
        s.send(data)
        print("\n[*] Recebendo Dados...")
        while 1:
            reply = s.recv(TAMANHO_BUFFER)
            
            if len(reply) > 0:
                # Enviando resposta recebida ao cliente solicitante
                conn.sendall(reply)
                print("\n[*] Resposta de requisição enviada ao cliente: {} > {}".format(webserver, addr[0]))
            else:
                print("\n[*] Dados obtidos com sucesso...")
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