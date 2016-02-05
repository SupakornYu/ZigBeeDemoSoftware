import logging
import threading
import time
import Queue


class ZigBeeDESC(object):

    def __init__(self,globalnetworkid_instance,toSerial_Queue):

        self.queryActiveEndpoints_queue = Queue.Queue()
        self.queryCluster_queue = Queue.Queue()
        self.globalnetworkid_instance = globalnetworkid_instance
        self.toSerial_Queue_instance = toSerial_Queue

        self.processActiveEndpoints_thread = threading.Thread(target=self.processActiveEndpoints)
        self.processActiveEndpoints_thread.start()

        self.processClusters_thread = threading.Thread(target=self.processClusters)
        self.processClusters_thread.start()

        logging.debug('ZigBee DESC init')

    def queryActiveEndpoints(self,networkAddress):
        self.putCMDToSerialQueue("getActiveEndpoints "+str(networkAddress))

    def queryClusters(self,networkAddress,ep):
        self.putCMDToSerialQueue("getSimpleDesc "+str(networkAddress)+" "+str(ep))

    #run as thread
    def processActiveEndpoints(self):
        while True:
            temp = ''
            temp = self.queryActiveEndpoints_queue.get()
            print "in processActiveEndpoints"
            if temp.split()[0] == '<|ActiveEndPoints':
                nwk_temp = temp.split(',')[1]
                for dd in temp.split('<|')[2].split('|'):
                    self.queryClusters(nwk_temp,dd)

    def processClusters(self):
        while True:
            temp = ''
            temp = self.queryCluster_queue.get().rstrip()
            print "in processClusters"
            if temp.split()[0] == '<|QueryCluster':
                nwk_temp = temp.split(',')[1]
                ep_temp = temp.split(',')[3].split(':')[1]
                APID_temp = temp.split(',')[4].split(':')[1]
                ADID_temp = temp.split(',')[5].split(':')[1]
                GBID_temp = self.globalnetworkid_instance.getGlobalId(1,str(nwk_temp))[0]
                print str('GBID')+str(GBID_temp)

                inCluster_temp = [dd for dd in temp.split('<|')[2].split('|')]
                inCluster_temp.pop(0)


                outCluster_temp = [dd for dd in temp.split('<|')[3].split('|')]
                outCluster_temp.pop(0)

                self.globalnetworkid_instance.addDescDevice(GBID_temp,ep_temp,APID_temp,ADID_temp,inCluster_temp,outCluster_temp)

                self.globalnetworkid_instance.updateNodeDescTable()
                #send task to report Routine here

    def putCMDToSerialQueue(self,cmd):
        cmd = cmd+"\r\n"
        cmd = cmd.encode('ascii')
        self.toSerial_Queue_instance.put(cmd)
        # print cmd