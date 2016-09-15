# tcp client programm
from socket import *


HOST = 'localhost'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)

import thread
import threading
con = threading.Condition()
msg_list = list()
def client_thread(no, msg_list):
    while True:
        data1 = tcpCliSock.recv(BUFSIZ)
        if not data1:
            continue
        print data1
        if con.acquire():
            msg_list.append(data1)
            con.release()
    thread.exit_thread()


def test_thread(): #Use thread.start_new_thread() to create 2 new threads
    thread.start_new_thread(client_thread, (1,msg_list))


test_thread()
while True:
    data1= raw_input(">")
    if tcpCliSock:
        tcpCliSock.send(data1)

tcpCliSock.close()