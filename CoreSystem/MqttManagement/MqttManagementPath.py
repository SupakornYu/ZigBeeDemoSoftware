MQTT_SERVER_IP = "188.166.233.211"
MQTT_SERVER_PORT = 1883
MQTT_SERVER_KEEPALIVE = 60

GLOBAL_ID_TOPIC_SEND = 'multiProtocolGateway/Demo/toMQTT/GlobalId'
GLOBAL_DESC_NODE_SEND = 'multiProtocolGateway/Demo/toMQTT/GlobalDESC'

CORE_REPORT_VALUE_TO_MQTT = 'multiProtocolGateway/Demo/toMQTT/Report'
CORE_CMD_FROM_CLIENT = 'multiProtocolGateway/Demo/fromMQTT/CMD'

ESP8266_REGISTER_NEW_DEVICE_TOPIC_GET = 'multiProtocolGateway/Demo/fromMQTT/ESP8266/registerNewDevice'
ESP8266_CMD_FROM_CORE_TO_NODE_SEND = 'multiProtocolGateway/Demo/toMQTT/ESP8266/CMD' #+ChipID
ESP8266_REPORT_FROM_NODE_TO_CORE_GET = 'multiProtocolGateway/Demo/toMQTT/ESP8266/REPORT'