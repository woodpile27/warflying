from scapy.all import *
from impacket import ImpactDecoder
import pymongo
import redis
import time
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


def sniff_AP():
    sniff(iface='mon0', prn=save_to_redis, filter='wlan[0]==0x80 or wlan[0]==0x50')


def save_to_redis(pkt):
    data = '||'.join(str(i) for i in [pkt, gpsd.fix.latitude, gpsd.fix.longitude])
    try:
        REDIS.rpush("wifi", data)
    except Exception,e:
        print e
        print 'save to redis failed'


def get_from_redis():
    while True:
        try:
            data = REDIS.lpop("wifi")
            if data:
                pkt, lat, lng = data.split('||')
                pkt = RadioTap(pkt)
                parse(pkt, lat, lng)
            else:
                print 'wifi is empty'
                time.sleep(1)
        except:
            print 'error'


def parse(pkt, lat, lon):
    radio_packet = RTD.decode(str(pkt))
    _signal = radio_packet.get_dBm_ant_signal()
    if _signal:
        signal = _signal and -(256-_signal) or -120
    else:
        pass
    bssid = pkt[Dot11].addr2
    essid = pkt[Dot11Elt].info if pkt[Dot11Elt].info != '' else 'hidden essid'
    locate = [lat, lon, str(signal)]
    data = {'bssid': bssid,
            'essid': essid,
            'locate': ','.join(locate)
        }
    save_to_mongo(data)
            

def save_to_mongo(data):
    try:
        if mongodb['original_test_test'].update({'bssid': data['bssid']},{'$set': {'bssid': data['bssid'],'essid': data['essid']},'$push': {'locates': data['locate']}}, upsert=True):
            print 'save to mongodb successful'
    except Exception, e:
        print 'save to mongodb failed'
        print e
    

if __name__ == '__main__':
    RTD = ImpactDecoder.RadioTapDecoder()
    gpsp = GpsPoller()
    gpsp.start()
    threading.Thread(target=sniff_AP).start()
    threading.Thread(target=get_from_redis).start()

