#!/usr/bin/python3 -u

import zmq
import json
import zlib
import requests
from time import sleep

class EDDNListener():
    def __init__(self):
        self.eddnrelay = 'tcp://eddn.edcd.io:9500'
        self.eddntimeout = 600000

    def eddn_parser(self):
        ctx = zmq.Context()
        sub = ctx.socket(zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, b"")
        sub.setsockopt(zmq.RCVTIMEO, self.eddntimeout)
        while True:
            try:
                sub.connect(self.eddnrelay)
                while True:
                    msg = sub.recv()
                    if msg == False:
                        sub.disconnect(self.eddnrelay)
                        break
                    msg = zlib.decompress(msg)
                    jsonmsg = json.loads(msg)
                    if jsonmsg['$schemaRef'] == 'https://eddn.edcd.io/schemas/commodity/3':
                        for commodity in jsonmsg['message']['commodities']:
                            if commodity['name'] == 'lowtemperaturediamond':
                                stationname = jsonmsg['message']['stationName']
                                systemname = jsonmsg['message']['systemName']
                                sellprice = str(commodity['sellPrice'])
                                demand = str(commodity['demand'])
                                padsize = self.pad_size_check(systemname,stationname)
                                print(stationname + ', ' + systemname)
                                print('Sell price: ' + sellprice)
                                print('Demand: ' + demand)
                                print('Pad size: ' + padsize)
                                print('--------')
                    else:
                        continue
            except zmq.ZMQError as e:
                print('ZMQSocketException: ' + str(e))
                sub.disconnect(self.eddnrelay)
                sleep(5)
            break

    def pad_size_check(self,system,station):
        r = requests.get('https://www.edsm.net/api-system-v1/stations?systemName=' + system)
        jsonmsg = json.loads(r.text)
        for entry in jsonmsg['stations']:
            if entry['name'] == station:
                if 'outpost' in entry['type'].lower():
                    size = 'M'
                    return size
                else:
                    size = 'L'
                    return size

EDDNListener = EDDNListener()
EDDNListener.eddn_parser()
