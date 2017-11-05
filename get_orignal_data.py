from scapy.all import *
from impacket import ImpactDecoder
import pymongo
import redis
import time
import os
from itertools import cycle
from gps import *
import threading


REDIS = redis.Redis(host='localhost', port=6379)
mongo_client = pymongo.MongoClient('localhost')
mongodb = mongo_client['wifi_maps']
gpsd = None


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd
        gpsd = gps(mode=WATCH_ENABLE)
        self.current_value = None
        self.running = True

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next()


def parse(pkt):
    radio_packet = RTD.decode(str(pkt))
    _signal = radio_packet.get_dBm_ant_signal()
    if _signal:
        signal = _signal and -(256-_signal) or -120
    else:
        pass
    bssid = pkt[Dot11].addr2
    essid = pkt[Dot11Elt].info if pkt[Dot11Elt].info != '' else 'hidden essid'
    locate = [gpsd.fix.latitude, gpsd.fix.longitude, signal]
    data = {'bssid': bssid,
            'essid': essid,
            'locate': ','.join(str(i) for i in locate)
        }
    save_to_redis(data)
            

def save_to_redis(data):
    try:
        REDIS.rpush("wifi", data)
    except:
        print 'save to redis failed'


def save_to_mongo():
    while True:
        try:
            data = eval(REDIS.lpop("wifi"))
        except:
            print 'wifi is empty...'
            time.sleep(1)
            save_to_mongo()
        try:
            if mongodb['original'].update({'bssid': data['bssid']},{'$set': {'bssid': data['bssid'],'essid': data['essid']},'$push': {'locates': data['locate']}}, upsert=True):
                print 'save to mongodb successful'
        except Exception, e:
            print 'save to mongodb failed'
            print e
    

def sniff_AP():
    sniff(iface='mon0', prn=parse, filter='wlan[0]==0x80')

    
def change_channel():
    for ch in cycle([1,3,5,7,9,11,13]):
        os.system('sudo iwconfig wlan1mon channel ' + str(ch))
        time.sleep(0.5)

if __name__ == '__main__':
    RTD = ImpactDecoder.RadioTapDecoder()
    gpsp = GpsPoller()
    gpsp.start()
    threading.Thread(target=sniff_AP).start()
    threading.Thread(target=change_channel).start()
    threading.Thread(target=save_to_mongo).start()

