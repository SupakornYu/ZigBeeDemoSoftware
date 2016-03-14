#Copyright (c) 2015 Supakorn Yukonthong

import serial
import threading
import json
import time

#use quene list to get data from serial and add to quene list 
#the function that have duty to use data to process should get from quene
#To prevent threading process data at the same time you should lock a quene

def initSerial():
    sp = serial.Serial()
    sp.port = 'COM10'
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
        #while data_left>=0:
        #print type(value)
        #slice with \r\n to list
        if data_left>0:
            value = ser.read(data_left)
            print value
            '''
            for i in value:
                _temp+=i
                if i=='\n':
                    _cmdList.append(_temp)
                    _temp = ''
            for i in _cmdList:
                print i
            '''
        #if len(value)>0:
        #   print value

def writeCommandToSerial(ser,cmd):
    cmd = cmd+"\r\n"
    cmd = cmd.encode('ascii')
    ser.write(cmd)


if __name__ == '__main__':
    
    sp = initSerial()
    print sp

    #sp.write("help\r\n".encode('ascii'))

    t1 = threading.Thread(target=readInputSerial,args=(sp,))
    t1.start()
    #value = sp.readline()
    #print value
    
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
