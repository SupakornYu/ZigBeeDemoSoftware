import logging
import threading
import time
import paho.mqtt.client as mqtt
#sys.path.append('../MqttManagement')
#print os.path.abspath(os.path.dirname(__file__) + '/' + '../..')
#sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from CoreSystem.MqttManagement import MqttManagementPath
import json
import GlobalTableCache


logging.basicConfig(level=logging.DEBUG)


class GlobalNetworkIdManagement(object):
    #GBID 0 is reserved
    #globalTable [globalId,deviceTechType,localNetworkId]
    def __init__(self,start=1):

        #loading GBID from mongodb cache
        self.GlobalTableCache_instance = GlobalTableCache.GlobalTableCache()
        if self.GlobalTableCache_instance.getGBIDCount() != None:
            self.temp_GBIDCount = self.GlobalTableCache_instance.getGBIDCount()
        else:
            self.temp_GBIDCount = start
            self.GlobalTableCache_instance.updateGBIDCount(self.temp_GBIDCount)

        self.pathMqttGlobalTable = MqttManagementPath.GLOBAL_ID_TOPIC_SEND
        self.pathMqttNodeDescTable = MqttManagementPath.GLOBAL_DESC_NODE_SEND
        self.MQTTclient = mqtt.Client()
        self.startMQTTserver()

        self.lock = threading.Lock()


        self.globalId = self.temp_GBIDCount

        self.globalTable = []
        self.nodeDescTable = []
        logging.debug('GlobalNetworkIdManagement init')

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
        self.MQTTclient.publish(self.pathMqttGlobalTable,json.dumps(self.globalTable),0,True)

    def updateNodeDescTable(self):
        self.MQTTclient.publish(self.pathMqttNodeDescTable,json.dumps(self.nodeDescTable),0,True)

    #deviceTechType zigbeeHA=1,ESP8266=2
    def registerNewDevice(self,deviceTechType,localNetworkId,uniqueValue):
        #logging.debug('Waiting for lock')
        self.lock.acquire()
        try:
            #logging.debug('Acquired lock')
            if [d for d in self.globalTable if d[1] ==deviceTechType and d[2] ==localNetworkId] == []:
                tempRow = []
                #get GBID from cache
                temp_GBIDFromCache = self.GlobalTableCache_instance.getGBIDCache(deviceTechType,uniqueValue)
                if temp_GBIDFromCache != None:
                    tempRow = [temp_GBIDFromCache,deviceTechType,localNetworkId]
                else:
                    tempRow = [self.globalId,deviceTechType,localNetworkId]
                    self.GlobalTableCache_instance.addNewDevice(self.globalId,deviceTechType,uniqueValue)
                    self.globalId = self.globalId + 1
                    self.GlobalTableCache_instance.updateGBIDCount(self.globalId)
                self.globalTable.append(tempRow)

            #else:
                #logging.debug('Already contained')
        finally:
            self.lock.release()

    def getGlobalTable(self):
        return  self.globalTable

    def getRealIdByGlobalId(self,globalId):
        return [d for d in self.globalTable if d[0] == globalId]

    def getGlobalId(self,deviceTechType,localNetworkId):
        return [d for d in self.globalTable if d[1] == deviceTechType and d[2] == localNetworkId]

    def delDeviceFromGlobalTable(self,deviceTechType,localNetworkId):
        '''
        print "delDeviceFromGlobalTable"
        print deviceTechType
        print localNetworkId
        '''
        self.globalTable = [d for d in self.globalTable if not(d[1] ==deviceTechType and d[2] ==localNetworkId)]

    def addDescDevice(self,GBID,EP,APID,ADID,ClusterIn,ClusterOut):
        #check duplicate if true record should be updated
        if [d for d in self.nodeDescTable if d['GBID']==GBID and d['EP']==EP] == []:
            self.nodeDescTable.append({'GBID':GBID,'EP':EP,'APID':APID,'ADID':ADID,'ClusterIn':ClusterIn,'ClusterOut':ClusterOut})
            logging.debug('Add DESC success')
        else:
            #update record not add a new one
            self.nodeDescTable = [d for d in self.nodeDescTable if not(d['GBID']==GBID and d['EP']==EP)]
            self.nodeDescTable.append({'GBID':GBID,'EP':EP,'APID':APID,'ADID':ADID,'ClusterIn':ClusterIn,'ClusterOut':ClusterOut})
            logging.debug('Already contained')

    def delDescDevice(self,GBID):
        self.nodeDescTable = [d for d in self.nodeDescTable if d['GBID'] != GBID]

    #deviceTechType all=0,zigbeeHA=1,ESP8266=2
    def cleanGlobalTable(self,deviceTechType):
        if deviceTechType == 0:
            self.globalTable = []
        elif deviceTechType == 1:
            self.globalTable = [d for d in self.globalTable if d[1] !=1]
        elif deviceTechType == 2:
            self.globalTable = [d for d in self.globalTable if d[1] !=2]

    def getNodeDESCTable(self):
        return self.nodeDescTable

    def getEPFromNodeDESCTable(self,GBID,ClusterId):
        temp = [dd for dd in self.nodeDescTable if dd['GBID'][0] == int(GBID) and str(ClusterId) in dd['ClusterIn']]
        #always return first ep
        if  temp != []:
            return str(temp[0]['EP'])
        return []

    def cleanNodeDescTable(self):
        self.nodeDescTable = []

    def cleanNodeDescTableWithDeviceType(self,deviceTechType):
        if self.nodeDescTable != []:
            if deviceTechType == 0:
                self.nodeDescTable = []
            elif deviceTechType == 1:
                self.nodeDescTable = [d for d in self.nodeDescTable if d['GBID'][1] !=1]
            elif deviceTechType == 2:
                self.nodeDescTable = [d for d in self.nodeDescTable if d['GBID'][1] !=2]

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