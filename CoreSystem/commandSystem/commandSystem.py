import logging
import threading
import time
import Queue
import paho.mqtt.client as mqtt
from CoreSystem.MqttManagement import MqttManagementPath
import json

class CommandSystem(object):
#class CommandSystem(object):

    def __init__(self,globalnetworkid_instance,flagTopologyRunner_list,report_instance,toSerial_Queue):
        self.pathMqttCMDFromClient = MqttManagementPath.CORE_CMD_FROM_CLIENT
        self.cmdToESP8266 = MqttManagementPath.ESP8266_CMD_FROM_CORE_TO_NODE_SEND
        self.MQTTclient = mqtt.Client()
        self.startMQTTserver()

        self.globalnetworkid_instance = globalnetworkid_instance
        self.flagTopologyRunner_list = flagTopologyRunner_list
        self.report_instance = report_instance
        self.toSerial_Queue_instance = toSerial_Queue

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        #client.subscribe("/ZigBeeAtmel/toMQTT")
        #Clear Topic Message
        self.MQTTclient.publish(self.pathMqttCMDFromClient,json.dumps([]),0,True)
        client.subscribe(self.pathMqttCMDFromClient)
        #client.subscribe(self.pathMqtt)

    def on_message(self,client, userdata, msg):
        print msg.topic+" "+msg.payload
        if msg.topic == self.pathMqttCMDFromClient:
            temp_list_payload = json.loads(msg.payload)
            for i in temp_list_payload:
                GBID_temp = i['GBID']
                value_temp = i['VALUE']
                CMD_temp = i['CMD']
                nwk_temp = self.globalnetworkid_instance.getRealIdByGlobalId(int(GBID_temp))
                print 'DEBUG CMD : '+str(nwk_temp)
                if nwk_temp != []:
                    nwk_temp = nwk_temp[0]
                    if CMD_temp == '0001':
                        #you have to query and get endpoint from node desc because we do not know onoff cluster run on
                        #which ep but now we assign to 0x11 == ep 17
                        if nwk_temp[1] == 1:
                            value_temp = "-on" if value_temp == '1' else "-off"
                            EP_temp = self.globalnetworkid_instance.getEPFromNodeDESCTable(nwk_temp[0],6)
                            print EP_temp
                            EP_temp = str(EP_temp) if EP_temp != [] else "0xff"
                            #0x11
                            self.putCMDToSerialQueue('onOff 0x02 '+str(nwk_temp[2])+' '+EP_temp+' "'+value_temp+'"')
                            print 'DEBUG CMD : ZigBee -> '+str(value_temp)


                        elif nwk_temp[1] == 2:
                            CMD_message_MQTT = [{"MACADDR":str(nwk_temp[2]),"CMD":"0001","VALUE":value_temp}]
                            #print self.cmdToESP8266+'/'+str(nwk_temp[2])
                            self.MQTTclient.publish(self.cmdToESP8266+'/'+str(nwk_temp[2]),json.dumps(CMD_message_MQTT),0,True)
                            print 'DEBUG CMD : ESP -> '+str(nwk_temp[2])

                        #cheating here
                        print "report Table : "+str(self.report_instance.getReportTable())
                        self.report_instance.addReportDataTable(nwk_temp,'On/Off',i['VALUE'])
                        self.report_instance.updateReportTableToMQTT()
                    elif CMD_temp == '0004':
                        #you have to query and get endpoint from node desc because we do not know onoff cluster run on
                        #which ep but now we assign to 0x11 == ep 17
                        if nwk_temp[1] == 1:
                            EP_temp = self.globalnetworkid_instance.getEPFromNodeDESCTable(nwk_temp[0],3)
                            print EP_temp
                            EP_temp = str(EP_temp) if EP_temp != [] else "0xff"
                            self.putCMDToSerialQueue('identify 0x02 '+str(nwk_temp[2])+' '+EP_temp+' "'+value_temp+'"')
                            print 'DEBUG CMD : ZigBee -> '+str(value_temp)


                        elif nwk_temp[1] == 2:
                            CMD_message_MQTT = [{"MACADDR":str(nwk_temp[2]),"CMD":"0004","VALUE":value_temp}]
                            #print self.cmdToESP8266+'/'+str(nwk_temp[2])
                            self.MQTTclient.publish(self.cmdToESP8266+'/'+str(nwk_temp[2]),json.dumps(CMD_message_MQTT),0,True)
                            print 'DEBUG CMD : ESP -> '+str(nwk_temp[2])



                #for global config GBID = 0
                elif GBID_temp == '0':
                    if CMD_temp =='0002':
                        if value_temp =='1':
                            self.report_instance.setReportFlagRunner(False)
                            self.flagTopologyRunner_list[0] = True

                            self.putCMDToSerialQueue('startEzMode')

                        elif value_temp =='0':
                            self.report_instance.setReportFlagRunner(True)
                            self.flagTopologyRunner_list[0] = False

    def putCMDToSerialQueue(self,cmd):
        cmd = cmd+"\r\n"
        cmd = cmd.encode('ascii')
        self.toSerial_Queue_instance.put(cmd)

    def startMQTTserver(self):
        self.MQTTclient.on_connect = self.on_connect
        self.MQTTclient.on_message = self.on_message
        self.MQTTclient.connect(MqttManagementPath.MQTT_SERVER_IP, MqttManagementPath.MQTT_SERVER_PORT, MqttManagementPath.MQTT_SERVER_KEEPALIVE)
        self.MQTTclient.loop_start()

