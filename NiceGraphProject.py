import socket
import queue
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style 

Host = '192.168.43.133'
Port = 44445
    
def animate(i,graphPWM,connectionQueue,graphPWMListLeft,graphPWMListRight,data_count,graphMCP):
    if not connectionQueue.empty():
        dataReceived = connectionQueue.get()
        
        if len(graphPWMListLeft) == 50:
            graphPWMListLeft.pop(0)
            graphPWMListRight.pop(0)
            data_count.pop(0)
        
        graphPWMListLeft.append(int(float(dataReceived[5]))) 
        graphPWMListRight.append(int(float(dataReceived[7])))
        data_count.append(int(float(dataReceived[8])))
        
        if len(data_count) > 2:
            graphPWM.clear()
            graphPWM.set(ylabel='Duty Cycle',xlabel='Time',title='Car speed')
            graphPWM.set_ylim([-25,105])
            graphPWM.set_xlim([data_count[0], data_count[-1]])
            plot1, = graphPWM.plot(data_count,graphPWMListLeft,'r', label='Left motors')
            plot2, = graphPWM.plot(data_count,graphPWMListRight,'g', label='Right motors')
            graphPWM.legend(handles=[plot1,plot2],bbox_to_anchor=(0.8, 1.22), loc=2, borderaxespad=0.2)
            
            percentage = float(dataReceived[1])
            
            graphMCP.clear()
            graphMCP.set(ylabel='Percentage',title='Battery')
            graphMCP.set_ylim([0,100])
            graphMCP.bar('',percentage)

def connector(connection,connectionQueue):
    while True:
        receivedData = connection.recv(160)
        dataReceived = receivedData.decode('utf-8')
        dataReceived = dataReceived[1:-1].split(",")
        connectionQueue.put(dataReceived)
    
def main():        
    # style.use('fivethirtyeight')
    
    fig = plt.figure(figsize=(8,7))
    graphPWM = fig.add_subplot(2,1,1)
    graphMCP = fig.add_subplot(2,2,3)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((Host, Port))
    
    s.listen()
    connection, fromAddress = s.accept()

    graphPWMListLeft = []
    graphPWMListRight = []
    data_count = []
    
    connectionQueue = queue.Queue(0)
    
    connector_thread = threading.Thread(target=connector, args=(connection,connectionQueue)) 
    connector_thread.deamon = True
    connector_thread.start()
    
    ani = animation.FuncAnimation(fig, animate,fargs=(graphPWM,connectionQueue,graphPWMListLeft,graphPWMListRight,data_count,graphMCP), interval=10)
    plt.show()
    
    connection.close()

main()