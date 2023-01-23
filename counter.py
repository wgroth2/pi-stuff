#
# By Bill Roth, but I heavily used this as a reference. https://github.com/chrisys/background-radiation-monitor/blob/master/counter/counter.py
#

import time
import RPi.GPIO as GPIO
import datetime
from collections import deque
from influxdb_client import InfluxDBClient


counts = deque()
gPrint = True
usvh_factor = 1.0/151.0
gClient = None
gWriteApi = None

def countme(channel):
    global counts,gPrint
    timestamp = datetime.datetime.now()
    counts.append(timestamp)
    return

def setup():
    global gClient,gWriteApi

    if gPrint:
        print("running setup")
    GPIO.setmode (GPIO.BOARD)
    GPIO.setup(7, GPIO.IN)
    GPIO.add_event_detect(7, GPIO.FALLING, callback=countme)
    if gPrint:
        print("done with setup")
    gClient = InfluxDBClient(url="YOURINFLUXDBIPANDPORT", token='YOURINFLUXDB2TOKEN', org='YOUORG')
    gWriteApi = gClient.write_api()

    return

def sendDataPoint(p):
    '''send datapoint to the database'''
    global gWriteApi
    gWriteApi.write("radiation", "cottle",p)

    return

def main():
    global gPrint
    setup()

    loopCount = 0
    while True:
        loopCount += 1
        try:
            while counts[0] < datetime.datetime.now() - datetime.timedelta(seconds=60):
                counts.popleft()
        except IndexError:
            pass # there are no records in the queue.

        if loopCount == 10:
            loopCount=0
            microsieverts = len(counts)*usvh_factor
            measurements = [
              {
                'measurement': 'radiation',
                'fields': {
                    'cpm': int(len(counts)),
                    'usvh': microsieverts
                    }
               }
            ]
            if gPrint:
                print(measurements)
            sendDataPoint(measurements)

        time.sleep(1)

if __name__ == "__main__":
    main()
