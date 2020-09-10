#
# Pulling data from Purpleair and sending to Graphite by Python
#
# Core original code written by Durren Shen @durrenshen 
# in a blog at https://www.wavefront.com/weather-metrics/
# 
# Cleaned up by Bill Roth @BillRothVMware and rewritten.
#
import urllib2
import json
import logging
import socket
import sys
import time
import re
import syslog
import math

def print_output():
  #
  # Below assumes the proxy is running on the same system. YMMV
  #
  # Get epoch time 
  #
  epochtime = time.time()
  #
  # 
  try:
    f = urllib2.urlopen('https://www.purpleair.com/json?key=LWNB69ZWLY1NJOD3&show=60663')
  except urllib2.HTTPError, e:
    print('HTTPError = ' + str(e.code))
    quit(-1)
  
  json_string = f.read()
  parsed_json = json.loads(json_string)
  
  observation_epoch = parsed_json['results'][0]['LastSeen']
  sepochtime =  str(int(epochtime))
  print('weather.air_quality.glenwood.results.0.lastseen ' +  str(observation_epoch) + ' ' + sepochtime)
  
  LastUpdateCheck = parsed_json['results'][0]['LastUpdateCheck']
  print('weather.air_quality.glenwood.results.0.lastupdatecheck ' + str(LastUpdateCheck) + ' ' + sepochtime)
  
  Created = parsed_json['results'][0]['Created']
  print('weather.air_quality.glenwood.results.0.created ' + str(Created) + ' ' + sepochtime)
  
  Uptime = parsed_json['results'][0]['Uptime']
  print('weather.air_quality.glenwood.results.0.uptime ' + str(Uptime) + ' ' + sepochtime)
  
  RSSI = parsed_json['results'][0]['RSSI']
  print('weather.air_quality.glenwood.results.0.rssi ' + str(RSSI) + ' ' + sepochtime)
  
  Adc = parsed_json['results'][0]['Adc']
  print('weather.air_quality.glenwood.results.0.adc ' + str(Adc) + ' ' + sepochtime)
  
  p_0_3_um = parsed_json['results'][0]['p_0_3_um']
  print('weather.air_quality.glenwood.results.0.p_0_3_um ' + str(p_0_3_um) + ' ' + sepochtime)
  
  p_0_5_um = parsed_json['results'][0]['p_0_5_um']
  print('weather.air_quality.glenwood.results.0.p_0_5_um ' + str(p_0_5_um) + ' ' + sepochtime)
  
  p_1_0_um = parsed_json['results'][0]['p_1_0_um']
  print('weather.air_quality.glenwood.results.0.p_1_0_um ' + str(p_1_0_um) + ' ' + sepochtime)
  
  p_2_5_um = parsed_json['results'][0]['p_2_5_um']
  print('weather.air_quality.glenwood.results.0.p_2_5_um ' + str(p_2_5_um) + ' ' + sepochtime)
  
  p_5_0_um = parsed_json['results'][0]['p_5_0_um']
  print('weather.air_quality.glenwood.results.0.p_5_0_um ' + str(p_5_0_um) + ' ' + sepochtime)
  
  p_10_0_um = parsed_json['results'][0]['p_10_0_um']
  print('weather.air_quality.glenwood.results.0.p_10_0_um ' + str(p_10_0_um) + ' ' + sepochtime)
  
  pm1_0_cf_1 = parsed_json['results'][0]['pm1_0_cf_1']
  print('weather.air_quality.glenwood.results.0.pm1_0_cf_1 ' + str(pm1_0_cf_1) + ' ' + sepochtime)
  
  pm2_5_cf_1 = parsed_json['results'][0]['pm2_5_cf_1']
  print('weather.air_quality.glenwood.results.0.pm2_5_cf_1 ' + str(pm2_5_cf_1) + ' ' + sepochtime)
  
  pm10_0_cf_1 = parsed_json['results'][0]['pm10_0_cf_1']
  print('weather.air_quality.glenwood.results.0.pm10_0_cf_1 ' + str(pm10_0_cf_1) + ' ' + sepochtime)
  
  pm1_0_atm = parsed_json['results'][0]['pm1_0_atm']
  print('weather.air_quality.glenwood.results.0.pm1_0_atm ' + str(pm1_0_atm) + ' ' + sepochtime)
  
  pm2_5_atm = parsed_json['results'][0]['pm2_5_atm']
  print('weather.air_quality.glenwood.results.0.pm2_5_atm ' + str(pm2_5_atm) + ' ' + sepochtime)
  
  pm10_0_atm = parsed_json['results'][0]['pm10_0_atm']
  print('weather.air_quality.glenwood.results.0.pm10_0_atm ' + str(pm10_0_atm) + ' ' + sepochtime)
  
  humidity = parsed_json['results'][0]['humidity']
  print('weather.air_quality.glenwood.results.0.humidity ' + str(humidity) + ' ' + sepochtime)
  
  temp_f = parsed_json['results'][0]['temp_f']
  print('weather.air_quality.glenwood.results.0.temp_f ' + str(temp_f) + ' ' + sepochtime)
  
  pressure = parsed_json['results'][0]['pressure']
  print('weather.air_quality.glenwood.results.0.pressure ' + str(pressure) + ' ' + sepochtime)
  
  AGE = parsed_json['results'][0]['AGE']
  print('weather.air_quality.glenwood.results.0.AGE ' + str(AGE) + ' ' + sepochtime)
  
  
  aqi = calc_aqi(pm2_5_atm)
  print('weather.air_quality.glenwood.results.0.calc_pm25aqi_atm ' + str(int(round(aqi))) + ' ' + sepochtime)
  aqi = calc_aqi(p_2_5_um)
  print('weather.air_quality.glenwood.results.0.calc_pm25aqi_um ' + str(int(round(aqi))) + ' ' + sepochtime)
  aqi = calc_aqi(pm2_5_cf_1)
  print('weather.air_quality.glenwood.results.0.calc_pm25aqi_cf_1 ' + str(int(round(aqi))) + ' ' + sepochtime)
 
   
  syslog.syslog('Air Quality logged at ' + sepochtime)
  f.close()

def calc_aqi(inp):
  x = float(inp)
  #
  # attempted curve fit of AQI functoin. negative exponential based on https://www.airnow.gov/aqi/aqi-calculator/
  #
  ret = (0.0001 * x**3) - (0.0359 * x**2) + (4.1951*x)
  return ret
  
print_output()
