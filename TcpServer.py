from socket import *
from time import ctime

HOST = ''
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

def write2File(sent_str):
    writeSummaries = file('./text/conversation/sentences', 'a+')
    writeSummaries.write("\r\n")
    writeSummaries.write(str(sent_str))
    # writeSummaries.write("\r\n")
    writeSummaries.close()

while True:
    print 'waiting for connection...'
    tcpCliSock, addr = tcpSerSock.accept()
    print '...connected from:', addr

    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        tcpCliSock.send('[%s] %s' %(ctime(), data))
        write2File(data)
    tcpCliSock.close()

tcpSerSock.close()
