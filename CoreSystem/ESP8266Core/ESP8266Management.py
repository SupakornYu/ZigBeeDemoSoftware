import logging
import threading
import json
import time
import paho.mqtt.client as mqtt
from CoreSystem.MqttManagement import MqttManagementPath

from CoreSystem.GlobalNetworkIdSystem import GlobalNetworkIdManagement

logging.basicConfig(level=logging.DEBUG)

class ESP8266Management(object):
    def __init__(self,globalnetworkid_instance):

        self.globalnetworkid_instance = globalnetworkid_instance


        self.MQTTclient = mqtt.Client()
        self.startMQTTserver()
        logging.debug('ESP8266Management init')

    def on_connect(self,client, userdata, flags, rc):
        #print("Connected with result code "+str(rc))
        #client.subscribe("/ZigBeeAtmel/toMQTT")
        client.subscribe(MqttManagementPath.ESP8266_REGISTER_NEW_DEVICE_TOPIC_GET)
        client.subscribe(MqttManagementPath.ESP8266_REPORT_FROM_NODE_TO_CORE_GET)
        #client.subscribe(self.pathMqtt)

    def on_message(self,client, userdata, msg):
        #get data add to globaltable
        if msg.topic == MqttManagementPath.ESP8266_REGISTER_NEW_DEVICE_TOPIC_GET:
            self.globalnetworkid_instance.registerNewDevice(2,json.loads(msg.payload)['CHIPID'])
            self.globalnetworkid_instance.updateGlobalTableToMqtt()
        #print(msg.topic+" "+str(msg.payload))


    def startMQTTserver(self):
        self.MQTTclient.on_connect = self.on_connect
        self.MQTTclient.on_message = self.on_message
        self.MQTTclient.connect("188.166.233.211", 1883, 60)
        self.MQTTclient.loop_start()

    """
    def updateGlobalTableToMqtt(self):
        self.MQTTclient.publish(self.pathMqtt,json.dumps(self.globalTable),0,True)
    """

if __name__ == "__main__":
    logging.debug('test')
    test = GlobalNetworkIdManagement.GlobalNetworkIdManagement()
    testESP = ESP8266Management(test)
    while True:
        time.sleep(1)