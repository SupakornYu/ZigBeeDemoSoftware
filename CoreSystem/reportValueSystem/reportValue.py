import logging
import threading
import time
import Queue
import paho.mqtt.client as mqtt
from CoreSystem.MqttManagement import MqttManagementPath
import json
from datetime import datetime


class reportValue(object):

    def __init__(self,globalnetworkid_instance,toSerial_Queue,):

        self.reportFlagRunner = False

        self.pathMqttReport = MqttManagementPath.CORE_REPORT_VALUE_TO_MQTT
        self.pathMqttGetReportESP8266 = MqttManagementPath.ESP8266_REPORT_FROM_NODE_TO_CORE_GET
        self.MQTTclient = mqtt.Client()
        self.startMQTTserver()

        self.report_condition = threading.Condition()


        #self.repeatTime = 10 #seconds

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
        client.subscribe(self.pathMqttGetReportESP8266)


    def on_message(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        if msg.topic == self.pathMqttGetReportESP8266:
            temp_list_payload = json.loads(msg.payload)
            for i in temp_list_payload:
                try:
                    GBID_temp = self.globalnetworkid_instance.getGlobalId(2,i['MACADDR'])[0]
                    self.addReportDataTable(GBID_temp,'temperature',i['Temperature'])
                    self.addReportDataTable(GBID_temp,'Light',i['Light'])
                except Exception as e:
                    print "Please Regiter nodeMCU again MacAddr : "+str(i['MACADDR'])
                    print self.globalnetworkid_instance.getGlobalId(2,i['MACADDR'])
            self.updateReportTableToMQTT()

    def setReportFlagRunner(self,temp_flag):
        self.reportFlagRunner = temp_flag


    def startMQTTserver(self):
        self.MQTTclient.on_connect = self.on_connect
        self.MQTTclient.on_message = self.on_message
        self.MQTTclient.connect("188.166.233.211", 1883, 60)
        self.MQTTclient.loop_start()

    def taskZigBeeReportRunner(self):
        while True:
            while self.reportFlagRunner:
                print "Running ZigBee Report"
                temp_table = self.globalnetworkid_instance.getNodeDESCTable()
                #print "taskZigBeeReportRunner "+str(temp_table)
                if temp_table!=[]:
                    self.report_condition.acquire()
                    for i in temp_table:
                        if i['GBID'][1]==1:
                            for j in i['ClusterIn']:
                                if j == '1026':
                                    self.readAttributeZigBee(i['GBID'][2],i['EP'],j,0)
                                    self.report_condition.wait(10)
                                if j == '1280':
                                    self.readAttributeZigBee(i['GBID'][2],i['EP'],j,2)
                                    self.report_condition.wait(10)

                    self.report_condition.release()
                time.sleep(3)
            time.sleep(1)

    def cleandataReportTable(self):
        self.reportDataTable = []

    def addReportDataTable(self,GBID,ValueType,Value):
        if [dd for dd in self.reportDataTable if dd['GBID'] == GBID and ValueType in dd.keys() ] == []:
            self.reportDataTable.append({"GBID":GBID,str(ValueType):str(Value),"time":str(datetime.now())})
        else:
            self.reportDataTable = [dd for dd in self.reportDataTable if not(dd['GBID'] == GBID and ValueType in dd.keys() )]
            self.reportDataTable.append({"GBID":GBID,str(ValueType):str(Value),"time":str(datetime.now())})

        print 'from end report table :'+str(self.reportDataTable)

    def readAttributeZigBee(self,networkAddress,EP,clusterID,attributeID):
        cmd_temp = "readAttribute 0x02 "+str(networkAddress)+" "+str(EP)+" "+str(clusterID)+" "+str(attributeID)
        print cmd_temp
        self.putCMDToSerialQueue(cmd_temp)
        #print networkAddress

    def addStringToZigBeeReportQueue(self,valueString):
        self.attributeValueProcess_queue.put(valueString)

    def updateReportTableToMQTT(self):
        self.MQTTclient.publish(self.pathMqttReport,json.dumps(self.reportDataTable),0,True)

    #run as thread
    def processZigBeeReport(self):
        while True:
            temp = ''
            temp = self.attributeValueProcess_queue.get()

            try:
                if temp.split()[0] == '<-On/Off':
                    nwk_temp = temp.split('<-')[2].split(',')[1].rstrip()
                    OnOff_temp = temp.split('<-')[2].split(',')[0]
                    GBID_temp = self.globalnetworkid_instance.getGlobalId(1,str(nwk_temp))[0]
                    self.addReportDataTable(GBID_temp,'On/Off',OnOff_temp)
                else:
                    try:
                        self.report_condition.acquire()
                        print 'debug : '+str(temp)
                        print "in processZigBeeReport"
                        if temp.split()[0] == '<-ReadTemperature' and temp.split('<-')[2].split(',')[0] !='failed':
                            nwk_temp = temp.split('<-')[2].split(',')[1].rstrip()
                            temperature_temp = temp.split('<-')[2].split(',')[0]
                            GBID_temp = self.globalnetworkid_instance.getGlobalId(1,str(nwk_temp))[0]
                            self.addReportDataTable(GBID_temp,'temperature',temperature_temp)
                        elif temp.split()[0] == '<-ReadIasZone' and temp.split('<-')[2].split(',')[0] !='failed':
                            nwk_temp = temp.split('<-')[2].split(',')[2].rstrip()
                            ias_temp = temp.split('<-')[2].split(',')[1]
                            GBID_temp = self.globalnetworkid_instance.getGlobalId(1,str(nwk_temp))[0]
                            self.addReportDataTable(GBID_temp,'ias',ias_temp)
                        print self.reportDataTable
                        self.updateReportTableToMQTT()
                        self.report_condition.notify()
                        self.report_condition.release()
                    except Exception as ins:
                        print "ERROR REPORT WAIT : "+str(ins)
                        self.report_condition.notify()
                        self.report_condition.release()
            except Exception as ins:
                print "ERROR AUTO REPORT : "+str(ins)


    def getReportTable(self):
        return self.reportDataTable

    def putCMDToSerialQueue(self,cmd):
        cmd = cmd+"\r\n"
        cmd = cmd.encode('ascii')
        self.toSerial_Queue_instance.put(cmd)
        # print cmd