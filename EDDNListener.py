#!/usr/bin/python3 -u

import os
import zmq
import json
import zlib
import requests
from time import sleep
from datetime import datetime

class EDDNListener():
    def __init__(self):
        self.eddnrelay = 'tcp://eddn.edcd.io:9500'
        self.eddntimeout = 600000
        self.ltddict = {}
        self.opaldict = {}
        self.paindict = {}
        self.benidict = {}
        self.musgdict = {}
        self.grandict = {}
        self.seredict = {}
        self.minerals = [
            'lowtemperaturediamond',
            'opal',
            'painite',
            'benitoite',
            'musgravite',
            'grandidierite',
            'serendibite'
        ]

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
                        sendrequest = 0
                        for commodity in jsonmsg['message']['commodities']:
                            if commodity['name'] in self.minerals:
                                mineralname = commodity['name']
                                stationname = jsonmsg['message']['stationName']
                                systemname = jsonmsg['message']['systemName']
                                sellprice = commodity['sellPrice']
                                demand = commodity['demand']
                                if sendrequest == 0:
                                    padsize = self.pad_size_check(systemname,stationname)
                                    sendrequest += 1
                                recvtime = datetime.now()
                                self.add_to_dict(mineralname,stationname,systemname,sellprice,demand,padsize,recvtime)
                    else:
                        continue
            except zmq.ZMQError as e:
                print('ZMQSocketException: ' + str(e))
                sub.disconnect(self.eddnrelay)
                sleep(5)
            break

    def dict_trimmer(self,dictname):
        #Thank the stackoverflow gods for this gift of comprehension that I cannot comprehend.  REJOICE IN ITS FUNCTION!
        dictname = {k: v for k, v in sorted(dictname.items(), key=lambda item: item[1], reverse=True)}
        if len(dictname) > 10:
            i = 0
            tempdict = {}
            for key,value in dictname.items():
                tempdict[key] = value
                i += 1
                if i == 10:
                    break
            dictname = tempdict
        print(len(dictname))
        print('--------------------')
        for key,value in dictname.items():
            print(key,value)
        print('--------------------')


    def add_to_dict(self,mineral,station,system,sell,demand,pad,recvtime):
        if mineral == self.minerals[0]:
            print('ltd')
            self.ltddict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.ltddict)
        elif mineral == self.minerals[1]:
            print('opal')
            self.opaldict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.opaldict)
        elif mineral == self.minerals[2]:
            print('painite')
            self.paindict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.paindict)
        elif mineral == self.minerals[3]:
            print('benitoite')
            self.benidict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.benidict)
        elif mineral == self.minerals[4]:
            print('musgravite')
            self.musgdict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.musgdict)
        elif mineral == self.minerals[5]:
            print('grandidierite')
            self.grandict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.grandict)
        elif mineral == self.minerals[6]:
            print('serendibite')
            self.seredict[station + ',' + system] = [sell,demand,pad,recvtime]
            self.dict_trimmer(self.seredict)

    def pad_size_check(self,system,station):
        try:
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
        except:
            size = 'Unknown'
            return size

    def file_create_check(self):
        for commodity in self.minerals:
            if not os.path.exists(commodity):
                print('Generating file for ' + commodity)
                os.mknod(commodity)

    def cmdty_write(self,cmdty,station,system,sell,demand,pad):
        cmdtyfile = open(cmdty, 'a')
        cmdtyfile.write(station + ',' + system + ',' + str(sell) + ',' + str(demand) + ',' + pad + '\n')
        cmdtyfile.close()

EDDNListener = EDDNListener()
#EDDNListener.file_create_check()
EDDNListener.eddn_parser()
