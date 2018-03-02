 1 # -*- coding: utf-8 -*-
 2 """
 3 Created on Mon Mar 28 22:40:41 2016
 4 
 5 @author: zhanghc
 6 """
 7 
 8 import socket
 9 
10 s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
11 
12 s.connect(('127.0.0.1',9999))
13 
14 print s.recv(1024)
15 
16 for data in ['zhang','liu','wang']:
17     s.send(data)
18     print s.recv(1024)
19 
20 s.send('exit')
21 s.close()
