# genie2mqtt - Energenie EG-PMS-LAN to MQTT bridge, for use with home-assistant and other

Copyright: (c) 2018, Streltsov Sergey

Author: Streltsov Sergey (mailto:straltsou.siarhei@gmail.com, http://blablasoft.ru)

License: MIT

Version: 0.0.3 from 2018.04.04

Socket name length = 11 char

# The library translate Energenie socket state to MQTT server

tested only on EG-PMS-LAN

# Edit genie2mqtt.py file and set your data:

PM_IP = 'you_energenie_ip' - Energenie ip

PM_PASS = 'you_energenie_pass' - password for energenie access

MQTT_IP = 'you_mqtt_ip' - ip adress of mqtt broker

MQTT_USER = 'you_mqtt_username' - mqtt broker username

MQTT_PASS = 'you_mqtt_pass' - mqtt broker password

SCAN_INTERVAL = 600 - Energenie socket state scan interval, default 600 sec (10 min)

# Put genie2mqtt.py in autorun:

for Debian users, put files on /usr/local/etc/

create on etc/systemd/system file genie2mqtt.service

[Unit]
Description=Energenie to MQTT service daemon
After=network.target

[Service]
Type=simple
PIDFile=/var/run/genie2mqtt/genie2mqtt.pid
User=%i
OOMScoreAdjust=-100
ExecStart=/usr/local/etc/genie2mqtt.py -nolog
TimeoutStopSec=5
Restart=always

[Install]
WantedBy=multi-user.target
Alias=genie2mqtt.service

# Reload systemd daemon
systemctl daemon-reload
# Enable your service
systemctl enable genie2mqtt
# Start your service
systemctl start genie2mqtt
# Check service status
systemctl -l status genie2mqtt
