import socket

IPADDR = "127.0.0.1"
PORT = 45000

sk_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sk_server.bind((IPADDR, PORT))
sk_server.listen()

while True:
    try:
        sk_client, addr = sk_server.accept()  # クライアントの接続受付
        rcv_data = sk_client.recv(1024)
        if not rcv_data:
            print("receive data don't exist")
            break
        else:
            print("receive data : {} ".format(rcv_data.decode("utf-8")))
            sk_client.sendall('Device[1] : OK\n'.encode())


    except KeyboardInterrupt:
        sk_client.close()
        sk_server.close()
        break
