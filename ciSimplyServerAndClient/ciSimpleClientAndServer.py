import serial
import threading
import json
import time

from tornado import websocket, web, ioloop, gen

import Queue

toClient_Queue = Queue.Queue()
toCombine_Queue = Queue.Queue()
userClient = []

def writeCommandToClient(cmdClient):
    cmdClient = json.dumps(cmdClient)
    print 'writeCommandToClient : '+cmdClient
    for cl in userClient:
        cl.write_message(cmdClient)

def processSerialMessageToClient():
    while True:
        commandString = ''
        temp = ''
        temp = toClient_Queue.get();
        print "CQ : "+str(temp)
        if temp.count(':')==0:
            temp = temp.split(',')
            if temp[0]=='->Identify Query Response':
                temp = temp[1].split()
                addr = temp[2]
                commandString = {'cmd':'newDevice','type':'light','addr':addr}
                writeCommandToClient(commandString)
            else:
                commandString = {'cmd':'Other Message','message':temp}
                writeCommandToClient(commandString)
        elif temp.count(':')==1:
            temp = temp.split(':')
            cmdType = temp[0]
            params = temp[1]
            if cmdType=='<-Level Control Attr Report':
                params = params.split(',')
                paraValue = params[0].split()
                paraAddr = params[1].split()
                commandString = {'cmd':'reportLevelControl','type':'light','addr':paraAddr[2],'value':paraValue[2]}
                writeCommandToClient(commandString)
            elif cmdType=='<-On/Off Attr Report':
                params = params.split(',')
                paraValue = params[0].split()
                paraAddr = params[1].split()
                commandString = {'cmd':'reportOnOff','type':'light','addr':paraAddr[2],'value':paraValue[2]}
                writeCommandToClient(commandString)
            else:
                commandString = {'cmd':'Other Message','message':temp}
                writeCommandToClient(commandString)
        else:
            commandString = {'cmd':'Other Message','message':temp}
            writeCommandToClient(commandString)


def processMessageToSerial(ser):
    while True:
        commandString = ''
        temp = toCombine_Queue.get();
        try:
            jsonMessage = json.loads(temp)
            if jsonMessage['cmd']=='on/off':
                commandString = 'onOff 0x02 '+jsonMessage['addr']+' 0x11 "-'+jsonMessage['value']+'"'
                print commandString
                writeCommandToSerial(ser,commandString)
        except KeyError as ex:
            print ex
        '''
        except ValueError as ex:
            print ex
        except NameError as ex:
            print ex
        '''








class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("indexWebsocket.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print "Client is connecting : " + str(self)
        if self not in userClient:
            userClient.append(self)

    def on_message(self,message):
        print message
        toCombine_Queue.put(message)

    def on_close(self):
        if self in userClient:
            userClient.remove(self)

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value" : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
])

def webServerStarting():
    print "Start Server"
    app.listen(8888)
    ioloop.IOLoop.instance().start()










    

#use quene list to get data from serial and add to quene list 
#the function that have duty to use data to process should get from quene
#To prevent threading process data at the same time you should lock a quene

def initSerial():
    sp = serial.Serial()
    sp.port = 'COM3'
    sp.baudrate = 38400
    sp.parity = serial.PARITY_NONE
    sp.bytesize = serial.EIGHTBITS
    sp.stopbits = serial.STOPBITS_ONE
    sp.timeout = 0.5
    sp.xonxoff = False
    sp.rtscts = False
    sp.dsrdtr = False
    sp.open()
    return sp

def readInputSerial(ser):
    _temp = ''
    while True:
        time.sleep(1)
        data_left = ser.inWaiting()
        value = ''
        _cmdList = []
        #slice with \r\n to list
        if data_left>0:
            value = ser.read(data_left)
            for i in value:
                _temp+=i
                if i=='\n':
                    _cmdList.append(_temp)
                    toClient_Queue.put(_temp)
                    _temp = ''
            for i in _cmdList:
                print i
            
def writeCommandToSerial(ser,cmd):
    cmd = cmd+"\r\n"
    cmd = cmd.encode('ascii')
    ser.write(cmd)


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