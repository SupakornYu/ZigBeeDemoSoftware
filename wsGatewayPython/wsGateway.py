import threading
import json
import time

from tornado import websocket, web, ioloop, gen

import Queue

toClient_Queue = Queue.Queue()
toCombine_Queue = Queue.Queue()
webClient = []
ciClient = []





if __name__ == '__main__':

    sp = initSerial()
    print sp

    #sp.write("help\r\n".encode('ascii'))
    print "thread 1 : reading from serial"
    t1 = threading.Thread(target=readInputSerial,args=(sp,))
    t1.start()
    #value = sp.readline()
    #print value

    print "thread 2 : Starting Server"
    t2 = threading.Thread(target=webServerStarting)
    t2.start()


    print "thread 3 : processSerialMessageToClient"
    t2 = threading.Thread(target=processSerialMessageToClient)
    t2.start()


    print "thread 4 : processMessageToCombine"
    t2 = threading.Thread(target=processMessageToSerial,args=(sp,))
    t2.start()

    print "main thread : get input from user"
    while True:
        n = raw_input("Type Command : ")
        writeCommandToSerial(sp,n)

    #readInputSerial(sp)

    #sp.close()

    """
    print "hello"
    print json.dumps(['foo',{'key':'test'}])
    strTest = json.loads('["foo",{"key":"test"}]')
    print strTest[0]
    """