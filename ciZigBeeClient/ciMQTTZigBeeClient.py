import serial
import threading
import json
import time
import Queue
import paho.mqtt.client as mqtt
import sys
from CoreSystem.GlobalNetworkIdSystem import GlobalNetworkIdManagement
from CoreSystem.ESP8266Core import ESP8266Management
from CoreSystem.ZigBeeCore import ZigBeeDESC
from CoreSystem.reportValueSystem import reportValue

#for store string before send to mqtt
toMQTTServer_Queue = Queue.Queue()

stringFromSerial_Queue = Queue.Queue()
toCombine_ViaSerial_Queue = Queue.Queue()
processTopology_Queue = Queue.Queue()
nodes = []
links = []
routerList = [{'NWK id':0}]
hisRouterList = []

flagExecuteProcessTopology = False
queryTopology_condition = threading.Condition()
MQTTclient = mqtt.Client()

GlobalNetworkIdManagement_instance = GlobalNetworkIdManagement.GlobalNetworkIdManagement()
ESP8266Management_instance = ESP8266Management.ESP8266Management(GlobalNetworkIdManagement_instance)
ZigBeeDESC_instance = ZigBeeDESC.ZigBeeDESC(GlobalNetworkIdManagement_instance,toCombine_ViaSerial_Queue,queryTopology_condition)
reportValue_instance = reportValue.reportValue(GlobalNetworkIdManagement_instance,toCombine_ViaSerial_Queue)

#config Serial port
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
    sp.flushInput()
    sp.flushOutput()
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
                    stringFromSerial_Queue.put(_temp)
                    _temp = ''
            for i in _cmdList:
                print i

def writeCommandToSerial(ser):
    while True:
        temp = ''
        temp = toCombine_ViaSerial_Queue.get()
        print "CMD TO SERIAL :"+str(temp)
        ser.write(temp)
        time.sleep(0.1)
        # print temp

def addCommandToWriteSerialQueue(cmd):
    cmd = cmd+"\r\n"
    cmd = cmd.encode('ascii')
    toCombine_ViaSerial_Queue.put(cmd)
    # print cmd




def processMQTTQueue():
    while True:
        temp = ''
        #print 'in here'
        temp = toMQTTServer_Queue.get();
        #print temp
        MQTTclient.publish("/ZigBeeAtmel/toMQTT",temp,0,True)

def addDataToMQTTServerQueue(temp):
    toMQTTServer_Queue.put(temp)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("/ZigBeeAtmel/toMQTT")
    client.subscribe("/ZigBeeAtmel/toCi")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))




def startAndProcessMQTTClient():
    MQTTclient.loop_forever()

def deleteDictionaryFromList(temp,key,id):
    return [d for d in temp if d.get(key) != id]

def processTopology():
    routerList = [{'NWK id':0}]
    nodes = [{'NWK id': '0', 'LQI': '0', 'deviceType': '0'}]
    links = []
    hisRouterList = []
    flagExecuteProcessTopology = True
    print 'inside'
    while len(routerList)>0:
        print 'inside len while'
        flagKeepIndex = True
        routerNodeTemp = routerList.pop(0)
        #append for duplicate query
        hisRouterList.append(routerNodeTemp['NWK id'])
        print 'getTable '+str(routerNodeTemp['NWK id'])+' '+str(0)
        addCommandToWriteSerialQueue('getTable '+str(routerNodeTemp['NWK id'])+' '+str(0))
        nodeIndex = 0
        while flagKeepIndex == True:
            print 'get each row'
            temp = processTopology_Queue.get()
            temp = temp.split('|')
            if temp[1].split(',')[0].split(':')[0].split()[0]=='TableOfAddr' and temp[1].split(',')[1].split(':')[1].split()[0]!='0':
                print temp[1].split(',')[0].split(':')[0].split()
                #will add each node to list

                for i in range(2,len(temp)):

                    #filter sometime they will return coordinator address.
                    if not(int(temp[i].split(',')[0].split(':')[1].split()[0]) == 0 or (int(temp[i].split(',')[0].split(':')[1].split()[0]) in hisRouterList) or ({'NWK id':int(temp[i].split(',')[0].split(':')[1].split()[0])} in routerList)):
                        tempNode = {}
                        tempNode = {'NWK id':temp[i].split(',')[0].split(':')[1].split()[0],'LQI':temp[i].split(',')[1].split(':')[1].split()[0],'deviceType':temp[i].split(',')[3].split(':')[1].split()[0]}
                        tempLink = {}
                        tempLink = {'from':temp[1].split(',')[0].split(':')[1].split()[0],'to':temp[i].split(',')[0].split(':')[1].split()[0]}
                        nodes.append(tempNode)
                        links.append(tempLink)
                        if(int(temp[i].split(',')[3].split(':')[1].split()[0])==1):
                            if int(temp[i].split(',')[0].split(':')[1].split()[0]) not in hisRouterList:
                                print {'NWK id':int(temp[i].split(',')[0].split(':')[1].split()[0])}
                                routerList.append({'NWK id':int(temp[i].split(',')[0].split(':')[1].split()[0])})
                    print 'router List'
                    print routerList
                        #type query recursive
                        #0 for query more index
                        #1 for query more when router
                        #{'type':0,'NWK addr':22,index:0,numindex:4}
                        #{'type':1,'NWK addr':22}

                #under here for retriving if table have more than 2 list
                #by push command to queue with incresing index parameter
                #command to serial thread will get and execute its queue
                #spec on ZigBee retrive each round with 2 tuple
                if int(temp[1].split(',')[4].split(':')[1].split()[0]) > nodeIndex:
                    print 'node index '+str(nodeIndex)
                    nodeIndex+=2
                    addCommandToWriteSerialQueue('getTable '+str(routerNodeTemp['NWK id'])+' '+str(nodeIndex))
                else:
                    print 'else set flag '+str(nodeIndex)
                    flagKeepIndex = False
            else:
                flagKeepIndex = False

            print nodes
            print links

    dataSend = {'nodes':nodes,'links':links}
    addDataToMQTTServerQueue(json.dumps(dataSend))


    #clean nodeDESCTable


    #clean reportRoutineTable for preventing no device response

    #register zigbee device to global network id
    for row in dataSend['nodes']:
        GlobalNetworkIdManagement_instance.registerNewDevice(1,row['NWK id'])
        #add nkw_id to queryActiveEndpoint

        #add node count to query for counting and send mqtt unsuccess -1

    GlobalNetworkIdManagement_instance.updateGlobalTableToMqtt()
    ZigBeeDESC_instance.putNetworkAddressListToQueue(dataSend['nodes'])
    #class Query Desc startQuery method here and it will get global table and send address to serialport queue

    queryTopology_condition.acquire()
    queryTopology_condition.wait()
    flagExecuteProcessTopology = False
    queryTopology_condition.release()


def callGenTopologyEvery():
    while True:
        #have to push queue because we will recursive call processTopology
        if not(flagExecuteProcessTopology):
            processTopology()
        time.sleep(10)



def processCommandFromSerial():
    while True:
        commandString = ''
        temp = ''
        temp = stringFromSerial_Queue.get();
        print "String From Serial : "+str(temp)
        #print "CQ : "+str(temp)
        #if temp.count('|')>0:
        try:
            if temp.split()[0] == '<|TableOfAddr' or temp.split()[0] == '<|TableOfAddrBad':
                processTopology_Queue.put(temp)
            elif temp.split()[0] == '<|ActiveEndPoints' or temp.split()[0] == '<|ActiveEndPointUnSuccess':
                ZigBeeDESC_instance.queryActiveEndpoints_queue.put(temp)
            elif temp.split()[0] == '<|QueryCluster' or temp.split()[0] == '<|simpleDescRespUnSuccess':
                ZigBeeDESC_instance.queryCluster_queue.put(temp)

            elif temp.split()[0] == '<-ReadTemperature':
                reportValue_instance.addStringToZigBeeReportQueue(temp)
            elif temp.split()[0] == '<-ReadIasZone':
                reportValue_instance.addStringToZigBeeReportQueue(temp)
            elif temp.split()[0] == '<-On/Off':
                reportValue_instance.addStringToZigBeeReportQueue(temp)


        except Exception as inst:
            print "ERROR"
            print type(inst)
            print inst.args
            print inst
            print "Temp Value : "+str(temp)



            #     temp = temp[1].split()
            #     addr = temp[2]
            #     commandString = {'cmd':'newDevice','type':'light','addr':addr}
            #     writeCommandToClient(commandString)
            # else:
            #     commandString = {'cmd':'Other Message','message':temp}
            #     writeCommandToClient(commandString)



if __name__ == '__main__':

    sp = initSerial()
    print sp

    MQTTclient.on_connect = on_connect
    MQTTclient.on_message = on_message
    MQTTclient.connect("188.166.233.211", 1883, 60)
    #MQTTclient.publish("/ZigBeeAtmel/toMQTT", "Hello, World!",0,True)




    print "thread 1 : reading from serial"
    t1 = threading.Thread(target=readInputSerial,args=(sp,))
    t1.start()

    print "thread 2 : process queue write cmd to ci"
    t2 = threading.Thread(target=writeCommandToSerial,args=(sp,))
    t2.start()


    print "thread 3 : start and loopfoever MQTT Client"
    t3 = threading.Thread(target=startAndProcessMQTTClient)
    t3.start()

    print "thread 4 : process MQTT Client"
    t4 = threading.Thread(target=processMQTTQueue)
    t4.start()

    print "thread 5 : process Command From Serial"
    t5 = threading.Thread(target=processCommandFromSerial)
    t5.start()

    print "thread 6 : process Command From Serial"
    t6 = threading.Thread(target=callGenTopologyEvery)
    t6.start()


    # addDataToMQTTServerQueue('ddd')



    print "main thread : get input from user"
    while True:
        n = raw_input("Type Command : ")
        addCommandToWriteSerialQueue(n)