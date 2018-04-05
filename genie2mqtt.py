#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Streltsov Sergey
# Author: Streltsov Sergey (mailto:straltsou.siarhei@gmail.com, http://blablasoft.ru)
# License: MIT
# Version: 0.0.3 from 2018.04.04
# Socket name length = 11 char
"""
The library translate Energenie socket state to MQTT server
Supported models: genie.py library
tested only on EG-PMS-LAN
put genie2mqtt.py in autorun
"""

import paho.mqtt.client as mqtt
import genie
import time
import logging
from logging.handlers import RotatingFileHandler

PM_IP = '192.168.0.10' # ip address of your EG-PMS-LAN
PM_PASS = 'password' # password to access EG-PMS-LAN
MQTT_IP = '192.168.0.11' # ip address of mqtt broker
MQTT_USER = 'user' # user to access mqtt broker
MQTT_PASS = 'password' # password to access mqtt broker
SCAN_INTERVAL = 600 # scan interval in seconds
LOG_FILE = '/var/log/genie2mqtt.log' # path to log-file
# LOG_FILE = 'd:\\genie2mqtt.log' # for winwows users


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        client.subscribe('energenie/socket1/state/', 0)
        client.subscribe('energenie/socket2/state/', 0)
        client.subscribe('energenie/socket3/state/', 0)
        client.subscribe('energenie/socket4/state/', 0)
        client.energenie_logger.info('Connection established with code: {}'.format(rc))
    else:
        client.energenie_logger.info('Connection code: {}'.format(rc))
        # pass
        # print('connection error, try again...')


def on_message(client, userdata, msg):
    client.energenie_socket.toggle_pm(command=str(int(msg.payload)), socket=str(msg.topic[-8]))
    client.energenie_logger.info('message: {}'.format(msg.payload))
    client.energenie_socket.update(False)


def renew(client):
    if client.energenie_socket.online:
        isAvailable = 'online'
    else:
        isAvailable = 'offline'
    client.publish('energenie/name/', client.energenie_socket.name, 0)
    client.publish('energenie/ip/', client.energenie_socket.ip, 0)
    client.publish('energenie/mac/', client.energenie_socket.mac, 0)
    client.publish('energenie/online/', isAvailable, 0)
    client.publish('energenie/dhcp/', client.energenie_socket.dhcp, 0)
    client.publish('energenie/updated/', client.energenie_socket.updated, 0)
    client.publish('energenie/socket1/name/', client.energenie_socket.socket1['name'], 0)
    client.publish('energenie/socket2/name/', client.energenie_socket.socket2['name'], 0)
    client.publish('energenie/socket3/name/', client.energenie_socket.socket3['name'], 0)
    client.publish('energenie/socket4/name/', client.energenie_socket.socket4['name'], 0)
    client.publish('energenie/socket1/state/', str(client.energenie_socket.socket1['state']), 0)
    client.publish('energenie/socket2/state/', str(client.energenie_socket.socket2['state']), 0)
    client.publish('energenie/socket3/state/', str(client.energenie_socket.socket3['state']), 0)
    client.publish('energenie/socket4/state/', str(client.energenie_socket.socket4['state']), 0)
    client.energenie_logger.info('Socket is: {}'.format(isAvailable))


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
my_handler = RotatingFileHandler(LOG_FILE, mode='a', maxBytes=100*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)

p1 = genie.Energenie('http://'+PM_IP, PM_PASS)
p1.update(True)

mqtt.Client.connected_flag = False

mqttc = mqtt.Client()
mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
mqttc.energenie_socket = p1
mqttc.energenie_logger = app_log
mqttc.on_message = on_message
mqttc.on_connect = on_connect

try:
    mqttc.connect(MQTT_IP, 1883, 60)
    mqttc.loop_start()
except:
    mqttc.energenie_logger.error('Try reconnect...')
    # print('wait...')
    # mqttc.loop_stop()
    time.sleep(10)

while not mqttc.connected_flag:
    mqttc.energenie_logger.error('Connection with MQTT server not established...')
    time.sleep(5)

renew(mqttc)

while True:
    mqttc.energenie_socket.update(False)
    renew(mqttc)
    time.sleep(SCAN_INTERVAL)
