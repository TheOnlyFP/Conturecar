import socket

def main():
    try:
        host_ip = '192.168.3.14'
        host_port = 44445
        sock = servercreate(host_ip, host_port)
        while True:
            connection = serveracc(sock)
            print("Connection made \n")
            while True:
                data = b''
                data = connection.recv(160)
                data = data.decode('utf-8')
                timedata = data[1:-2]
                datalist = timedata.split(",")
                for i in datalist:
                    print(i)
                print("\n")
                if not data:
                    break
    except KeyboardInterrupt:
        connection.shutdown(socket.SHUT_RDWR)
        sock.close()
        print("socket closed")


def servercreate(host_ip, host_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host_ip, host_port))
    return sock

def serveracc(sock):
    sock.listen()
    connection, fadd = sock.accept()
    return connection
    
main()