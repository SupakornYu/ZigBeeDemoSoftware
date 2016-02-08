import logging
import threading
import time
import Queue
import paho.mqtt.client as mqtt
from CoreSystem.MqttManagement import MqttManagement
import json


class reportValue(object):

    def __init__(self,globalnetworkid_instance,toSerial_Queue):

        self.pathMqttReport = MqttManagement.CORE_REPORT_VALUE_TO_MQTT
        self.pathMqttGetReportESP8266 = MqttManagement.ESP8266_REPORT_FROM_NODE_TO_CORE_GET
        self.MQTTclient = mqtt.Client()
        self.startMQTTserver()


        self.repeatTime = 10 #seconds

        self.reportDataTable = []

        self.attributeValueProcess_queue = Queue.Queue()

        self.globalnetworkid_instance = globalnetworkid_instance
        self.toSerial_Queue_instance = toSerial_Queue

        self.taskZigBeeReportRunner_thread = threading.Thread(target=self.taskZigBeeReportRunner)
        self.taskZigBeeReportRunner_thread.start()

        self.processZigBeeReport_thread = threading.Thread(target=self.processZigBeeReport)
        self.processZigBeeReport_thread.start()

        logging.debug('ZigBee report init')

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

    def taskZigBeeReportRunner(self):
        while True:
            temp_table = self.globalnetworkid_instance.getNodeDESCTable()
            for i in temp_table:
                for j in i['ClusterIn']:
                    if j == '1026':
                        self.readAttributeZigBee(i['GBID'][2],i['EP'],j,0)
                    elif j == '1280':
                        self.readAttributeZigBee(i['GBID'][2],i['EP'],j,2)
            time.sleep(self.repeatTime)

    def cleandataReportTable(self):
        self.reportDataTable = []

    def addReportDataTable(self,GBID,ValueType,Value):
        if [dd for dd in self.reportDataTable if dd['GBID'] == GBID] == []:
            self.reportDataTable.append({"GBID":GBID,str(ValueType):str(Value)})
        else:
            self.reportDataTable = [dd for dd in self.reportDataTable if dd['GBID'] != GBID]
            self.reportDataTable.append({"GBID":GBID,str(ValueType):str(Value)})

    def readAttributeZigBee(self,networkAddress,EP,clusterID,attributeID):
        cmd_temp = "readAttribute 0x02 "+str(networkAddress)+" "+str(EP)+" "+str(clusterID)+" "+str(attributeID)
        print cmd_temp
        self.putCMDToSerialQueue(cmd_temp)
        print networkAddress

    def addStringToZigBeeReportQueue(self,valueString):
        self.attributeValueProcess_queue.put(valueString)

    def updateReportTableToMQTT(self):
        self.MQTTclient.publish(self.pathMqttReport,json.dumps(self.reportDataTable),0,True)

    #run as thread
    def processZigBeeReport(self):
        while True:
            temp = ''
            temp = self.attributeValueProcess_queue.get()
            print 'debug : '+str(temp)
            print "in processZigBeeReport"
            if temp.split()[0] == '<-ReadTemperature' and temp.split('<-')[2].split(',')[0] !='failed':
                nwk_temp = temp.split('<-')[2].split(',')[1].rstrip()
                temperature_temp = temp.split('<-')[2].split(',')[0]
                GBID_temp = self.globalnetworkid_instance.getGlobalId(1,str(nwk_temp))[0]
                self.addReportDataTable(GBID_temp,'temperature',temperature_temp)
            #elif
            print self.reportDataTable
            self.updateReportTableToMQTT()


    def putCMDToSerialQueue(self,cmd):
        cmd = cmd+"\r\n"
        cmd = cmd.encode('ascii')
        self.toSerial_Queue_instance.put(cmd)
        # print cmd