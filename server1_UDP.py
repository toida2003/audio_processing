import socket

IPADDR = "127.0.0.1"
PORT = 45000

sk_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sk_server.bind((IPADDR, PORT))

while True:
    try:
        rcv_data, sk_client = sk_server.recvfrom(1024)  #UDP
        if not rcv_data:
            print("receive data don't exist")
            break
        else:
            print("receive data : {} ".format(rcv_data.decode("utf-8")))     

    except KeyboardInterrupt:
        sk_server.close()
        break
