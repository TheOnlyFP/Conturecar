import socket

def main():
    host_ip = '192.168.3.14'
    host_port = 44443
    sock = servercreate(host_ip, host_port)
    connection = serveracc(sock)
    print("Connection made \n")
    pack = ""
    data = b''
    while True:
        data = connection.recv(160)
        data=data.decode('utf-8')
        timedata = data[1:-2]
        datalist = timedata.split(",")
        print(datalist)
        if not data:
            break


def servercreate(host_ip, host_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host_ip, host_port))
    return sock

def serveracc(sock):
    sock.listen()
    connection, fadd = sock.accept()
    return connection
    
while True:
    main()