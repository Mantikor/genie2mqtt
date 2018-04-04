#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Streltsov Sergey
# Author: Streltsov Sergey (mailto:straltsou.siarhei@gmail.com, http://blablasoft.ru)
# License: MIT
# Version: 0.0.3 from 2017.04.04
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

PM_IP = 'http://you_energenie_ip'
PM_PASS = 'you_energenie_pass'
MQTT_IP = 'you_mqtt_ip'
MQTT_USER = 'you_mqtt_username'
MQTT_PASS = 'you_mqtt_pass'
SCAN_INTERVAL = 600


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        client.subscribe('energenie/socket1/state/', 0)
        client.subscribe('energenie/socket2/state/', 0)
        client.subscribe('energenie/socket3/state/', 0)
        client.subscribe('energenie/socket4/state/', 0)
    else:
        pass
        # print('connection error, try again...')


def on_message(client, userdata, msg):
    client.energenie_socket.toggle_pm(command=str(int(msg.payload)), socket=str(msg.topic[-8]))
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


p1 = genie.Energenie('http://'+PM_IP, PM_PASS)
p1.update(True)

mqtt.Client.connected_flag = False

mqttc = mqtt.Client()
mqttc.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
mqttc.energenie_socket = p1
mqttc.on_message = on_message
mqttc.on_connect = on_connect

while not mqttc.connected_flag:
    try:
        mqttc.connect(MQTT_IP, 1883, 60)
    except:
        # print('wait...')
        time.sleep(2)

renew(mqttc, p1)

mqttc.loop_start()
while True:
    mqttc.energenie_socket.update(False)
    renew(mqttc)
    time.sleep(SCAN_INTERVAL)
