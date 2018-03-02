#!/usr/bin/env python
#-*- coding:utf-8 -*-

from socket import *
from time import ctime

host = ''
port = 8888
buffsize = 2048
ADDR = (host,port)

tctime = socket(AF_INET,SOCK_STREAM)
tctime.bind(ADDR)
tctime.listen(3)

while True:
    print('Wait for connection ...')
    client,addr = tctime.accept()
    print("Connection from :",addr)

    while True:
        data = client.recv(buffsize).decode()
        if not data:
            break
        else:
            print data
        #client.send(('[%s] %s' % (ctime(),data)).encode())
        client.send('yll')

    client.close()
client.close()
