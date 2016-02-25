from cx_Freeze import setup, Executable

setup( name = "MultiProtocolIotGateway",
       version = "0.1",
       description = "MultiProtocolIotGateway Project From CMU",
       executables = [Executable("ciMQTTZigBeeClient.py")])

#type python BuildciMQTTZigBeeClient.py build