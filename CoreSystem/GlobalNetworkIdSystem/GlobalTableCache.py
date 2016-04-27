from CoreSystem.MqttManagement import MqttManagementPath
from pymongo import MongoClient


class GlobalTableCache(object):
    def __init__(self):
        print MqttManagementPath.MONGODB_PATH
        self.mongodbClientInstance = MongoClient(MqttManagementPath.MONGODB_PATH)
        self.db = self.mongodbClientInstance.MPIGDEMO
        print self.db.GBIDTableCache

    #@staticmethod
    def updateGBIDCount(self,number):
        resp = self.db.GBIDTableCache.find_and_modify(
            query= { 'name': "GBIDCount"},
            update= { "$set": { 'GBIDCount': number } },
            upsert= True,
            full_response= True
        )

    def getGBIDCount(self):
        cursor = self.db.GBIDTableCache.find({'name': "GBIDCount"})
        print cursor[0]['GBIDCount'] if cursor.count()>0 else None
        return cursor[0]['GBIDCount'] if cursor.count()>0 else None

    def addNewDevice(self,GBID,deviceType,IEEEAddr):
        '''
        result = self.db.GBIDTableCache.insert_one(
            {
                "name": "nodeDetail",
                "GBID": GBID,
                "deviceType": deviceType,
                "IEEEAddr": IEEEAddr
            }
        )
        print result[0]
        '''
        resp = self.db.GBIDTableCache.find_and_modify(
            query= { "name": "nodeDetail","deviceType": deviceType,"IEEEAddr": IEEEAddr},
            update= { "$set": { "name": "nodeDetail","GBID": GBID,"deviceType": deviceType,"IEEEAddr": IEEEAddr } },
            upsert= True,
            full_response= True
        )

    #def removeDevice(self):

    def getGBIDCache(self,deviceType,IEEEAddr):
        cursor = self.db.GBIDTableCache.find({
                "name": "nodeDetail",
                "deviceType": deviceType,
                "IEEEAddr": IEEEAddr
            })
        print cursor[0]['GBID'] if cursor.count()>0 else None
        return cursor[0]['GBID'] if cursor.count()>0 else None


if __name__ == "__main__":
    GlobalTableCacheTest = GlobalTableCache()

    GlobalTableCacheTest.updateGBIDCount(2)
    GlobalTableCacheTest.getGBIDCount()
    GlobalTableCacheTest.addNewDevice(2,1,"0x1BB2011819250400")
    GlobalTableCacheTest.getGBIDCache(1,"0x1BB2011819250400")
