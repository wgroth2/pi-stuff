#
# Pulling data from Purpleair and sending to Graphite by Python
#
# Core original code written by Durren Shen @durrenshen 
# in a blog at https://www.wavefront.com/weather-metrics/
# 
# Cleaned up by Bill Roth @BillRothVMware, and bill.roth@gmail.com and rewritten.
#
import requests
import json
import socket
import syslog
import sys
import time
import re
import math
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

def write_measurement(measurements : list):
    client = InfluxDBClient(url="http://192.168.86.64:9998", token='mnJXTd770BwNKuVppP5sz5a1AxMT_NkAJR61qw3E1HVqCBMievv2a3VUsAT_A9RpTlfUVf1OOZi9PGIlCR4RzA==', org='cottle')
    write = client.write_api(write_options=SYNCHRONOUS)
    try:
        res = write.write(bucket="air", org="cottle", record=measurements,write_precision="s")
    except Exception as e:
      syslog.syslog(syslog.LOG_ERROR,str(e))
      sys.exit(1)
    client.close()

   

def print_output():
  #
  # Below assumes the proxy is running on the same system. YMMV
  #
  # Get epoch time 
  #
  epochtime = time.time()
  #
  # 

  key= {'X-API-Key' : 'F4769DAA-EB47-11EC-8561-42010A800005'}
  try:
    response = requests.get('https://api.purpleair.com/v1/sensors/60663', headers=key)
  except Exception as e:
    print(e)
    sys.exit(1)

  if response.status_code != 200:
      if response.status_code in (429,500):
          syslog.syslog(f"Error received {response.status_code}. Exiting quietly")
          sys.exit(0) # quietly ignore
      else:
         print(f'Error received: {response.status_code} : Text = {response.reason} {response.text}')
         sys.exit(1)

  parsed_json = response.json()
  measurements = [{
    'measurement' : 'air_quality',
    'tags': {'host' : socket.gethostname(),
              'where' : 'cottle' },
    'fields' : {'epochtime' : str(int(epochtime))}
  }]

  for i in parsed_json['sensor']:
    if i in ('stats', 'stats_a', 'stats_b'):
      pass
    else:
      measurements[0]['fields'][i] = parsed_json['sensor'][i]
  
  measurements[0]['time'] = parsed_json['data_time_stamp']
  write_measurement(measurements) 

  syslog.syslog(syslog.LOG_INFO, "Air quality logged at " + str(epochtime))

  # aqi = calc_aqi(pm2_5_atm)
   
  # syslog.syslog('Air Quality logged at ' + sepochtime)



def calc_aqi(inp):
  x = float(inp)
  #
  # attempted curve fit of AQI functoin. negative exponential based on https://www.airnow.gov/aqi/aqi-calculator/
  #
  ret = (-3E-13 * x**6) + (8E-10 * x**5) - (6E-07 * x**4) + (0.0002 * x**3) - (0.0434 * x**2) + (4.2234*x) + 1.2597
  return ret
  
def main():
  print_output()

if __name__ == "__main__":
    main()
