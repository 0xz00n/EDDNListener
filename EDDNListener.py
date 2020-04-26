#!/usr/bin/python3 -u

import sys
import zmq
import json
import zlib
from time import sleep

eddnrelay = 'tcp://eddn.edcd.io:9500'
eddntimeout = 600000

def main():
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, b"")
    sub.setsockopt(zmq.RCVTIMEO, eddntimeout)
    while True:
        try:
            sub.connect(eddnrelay)
            while True:
                msg = sub.recv()
                if msg == False:
                    sub.disconnect(eddnrelay)
                    break
                msg = zlib.decompress(msg)
                jsonmsg = json.loads(msg)
                if jsonmsg['$schemaRef'] == 'https://eddn.edcd.io/schemas/commodity/3':
                    for commodity in jsonmsg['message']['commodities']:
                        if commodity['name'] == 'lowtemperaturediamond':
                            print(jsonmsg['message']['stationName'] + ', ' + jsonmsg['message']['systemName'])
                            print('Sell price: ' + str(commodity['sellPrice']))
                            print('Demand: ' + str(commodity['demand']))
                            print('--------')
                else:
                    continue
        except zmq.ZMQError as e:
            print('ZMQSocketException: ' + str(e))
            sub.disconnect(eddnrelay)
            sleep(5)
        break

if __name__ == '__main__':
    main()
