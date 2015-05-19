#!/usr/local/bin/python
__author__ = 'lexx'
import telnetlib
import time
import re
import sys
import logging
import ConfigParser
from influxdb.influxdb08 import InfluxDBClient

configreader = ConfigParser.RawConfigParser()
configreader.read('qcheck.ini')
infuxdb_server_ip = configreader.get('settings', 'infuxdb.server.ip')
infuxdb_user = configreader.get('settings', 'influxdb.user')
influxdb_password = configreader.get('settings', 'influxdb.password')
influxdb_db = configreader.get('settings', 'influxdb.db')
yate_ip = configreader.get('settings', 'yateapi.ip')
db = InfluxDBClient(infuxdb_server_ip, 8086 ,infuxdb_user , influxdb_password, influxdb_db)

logger = logging.getLogger('qualitylogger')
hdlr = logging.FileHandler('quality.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger.addHandler(hdlr)
hdlr.setFormatter(formatter)
logger.setLevel(logging.DEBUG)


def checkprovider(provname,yate_ip):
  tn = telnetlib.Telnet(yate_ip,5038)
  tn.read_until(".\r\n")
  tn.write("output on\r\n")
  tn.write(("call analyzer/probe %s\r\n")%(provname))
  time.sleep(50)
  tn.write("drop analyzer\r\n")
  tn.write("quit\r\n")
  captured=tn.read_all()
  #print captured
  ree=re.findall(',(.*?)=([\d|\.]*)', captured,flags=re.MULTILINE)
  try:
  	gaps=str(ree[3][1])
  	gapslen=str(ree[4][1])
  	quality=str(ree[7][1])
  	total_time=str(ree[2][1])
  except:
	gaps=str(0)
	gapslen=str(0)
	quality=str(0)
	total_time=str(0)
  print "RESULT|"+gaps+"|"+gapslen+"|"+quality+"|"+total_time
  data = [{"points":[[float(gaps), float(gapslen), float(quality), float(total_time)]],  "name":"quality."+provname,   "columns":["gaps","gapslen","quality","total_time"]}]
  db.write_points(data)
  logger.info("Captured:%s"%(captured))

checklist = configreader.items("checklist")
for destination in checklist:
    destination = destination[1]
    checkprovider(destination,yate_ip)