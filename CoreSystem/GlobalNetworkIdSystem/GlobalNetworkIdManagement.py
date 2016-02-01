import logging
import threading
import time
import paho.mqtt.client as mqtt
import sys
import os
#sys.path.append('../MqttManagement')
#print os.path.abspath(os.path.dirname(__file__) + '/' + '../..')
#sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from CoreSystem.MqttManagement import MqttManagement
import json


logging.basicConfig(level=logging.DEBUG)


class GlobalNetworkIdManagement(object):
    #GBID 0 is reserved
    #globalTable [globalId,deviceTechType,localNetworkId]
    def __init__(self,start=1):

        self.pathMqtt = MqttManagement.GLOBAL_ID_TOPIC_SEND
        self.MQTTclient = mqtt.Client()
        self.startMQTTserver()

        self.lock = threading.Lock()
        self.globalId = start
        self.globalTable = []

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        #client.subscribe("/ZigBeeAtmel/toMQTT")
        client.subscribe("/ZigBeeAtmel/toCi")
        #client.subscribe(self.pathMqtt)

    def on_message(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))


    def startMQTTserver(self):
        self.MQTTclient.on_connect = self.on_connect
        self.MQTTclient.on_message = self.on_message
        self.MQTTclient.connect("188.166.233.211", 1883, 60)
        self.MQTTclient.loop_start()


    def updateGlobalTableToMqtt(self):
        self.MQTTclient.publish(self.pathMqtt,json.dumps(self.globalTable),0,True)

    #deviceTechType zigbeeHA=1,ESP8266=2
    def registerNewDevice(self,deviceTechType,localNetworkId):
        logging.debug('Waiting for lock')
        self.lock.acquire()
        try:
            logging.debug('Acquired lock')
            if [d for d in self.globalTable if d[1] ==deviceTechType and d[2] ==localNetworkId] == []:
                tempRow = []
                tempRow = [self.globalId,deviceTechType,localNetworkId]
                self.globalTable.append(tempRow)
                self.globalId = self.globalId + 1
            else:
                logging.debug('Already contained')
        finally:
            self.lock.release()

    def getGlobalTable(self):
        return  self.globalTable

    def getGlobalIdDetail(self,globalId):
        return [d for d in self.globalTable if d[0] == globalId]

    #deviceTechType all=0,zigbeeHA=1,ESP8266=2
    def cleanGlobalTable(self,deviceTechType):
        if deviceTechType == 0:
            self.globalTable = []
        elif deviceTechType == 1:
            self.globalTable = [d for d in self.globalTable if d[1] !=1]
        elif deviceTechType == 2:
            self.globalTable = [d for d in self.globalTable if d[1] !=2]

    #def deleteGlobalId(self,option,):






#testing
def tt(dd,deviceType):
    i=1
    while True:
        dd.registerNewDevice(deviceType,i)
        i+=1
        print dd.getGlobalTable()
        dd.updateGlobalTableToMqtt()
        time.sleep(1)







if __name__ == "__main__":
    logging.debug('test')
    print os.path.abspath(os.path.dirname(__file__) + '/' + '../..')

    """
    test = GlobalNetworkIdManagement()
    t1 = threading.Thread(target=tt, args=(test,1,))
    t1.start()
    t2 = threading.Thread(target=tt, args=(test,1,))
    t2.start()
    """