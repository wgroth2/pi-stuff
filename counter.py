#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import datetime
import sys
import syslog
import requests
from collections import deque

counts = deque()
gPrint = False
usvh_factor = 1.0/151.0
gDatapoints = 0
VM_URL = "http://192.168.0.107:8428/write"

def countme(channel):
    global counts, gPrint, gDatapoints
    timestamp = datetime.datetime.now()
    counts.append(timestamp)
    gDatapoints += 1
    if gDatapoints % 360 == 0:
        syslog.syslog(f'{gDatapoints} Written to database')
    return

def setup():
    if gPrint:
        print("running setup")
    syslog.syslog(f'{sys.argv[0]} Starting')
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.IN)
    GPIO.add_event_detect(7, GPIO.FALLING, callback=countme)
    if gPrint:
        print("done with setup")
    return

def sendDataPoint(cpm, usvh):
    '''send datapoint to VictoriaMetrics via InfluxDB line protocol'''
    data = f"radiation,location=2164Cottle cpm={cpm},usvh={usvh}"
    try:
        response = requests.post(VM_URL, data=data, timeout=5)
        if response.status_code != 204:
            syslog.syslog(f'VM write error: {response.status_code}')
    except requests.exceptions.RequestException as e:
        syslog.syslog(f'VM connection error: {e}')
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
            pass  # no records in queue

        if loopCount == 10:
            loopCount = 0
            microsieverts = len(counts) * usvh_factor
            cpm = int(len(counts))
            if gPrint:
                print(f"CPM: {cpm}  uSv/h: {microsieverts:.4f}")
            sendDataPoint(cpm, microsieverts)

        time.sleep(1)

if __name__ == "__main__":
    main()
