#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Streltsov Sergey
# Author: Streltsov Sergey (mailto:straltsou.siarhei@gmail.com, http://blablasoft.ru)
# License: MIT
# Version: 0.0.99 from 2017.08.20
# Socket name length = 11 char
"""
The library to toggle Energenie smart sockets.
Supported models: EG-PM2-LAN, EG-PMS2-LAN, EGM-PWM-LAN, EG-PMS2-WLAN, EG-PM1W-001
tested only on EG-PMS-LAN
"""

import json
import datetime
import requests


class Energenie(object):

    def __init__(self, ip, passwd):
        """
        Create and init an Energenie socket object
            Args:
                ip: ipv4 address of Energenie socket in the LAN
                passwd: password to socket access
        """
        # self.ip = self.__validate_ip__(ip)
        self.ip = ip
        self._passwd = passwd
        self.online = False
        self.mac = ''
        self.dhcp = False
        self.name = ''
        self.updated = ''
        self.socket1 = {'state': 0, 'name': ''}
        self.socket2 = {'state': 0, 'name': ''}
        self.socket3 = {'state': 0, 'name': ''}
        self.socket4 = {'state': 0, 'name': ''}

    def _login(self):
        """
        Login to Energenie socket
            Returns:
                Status code for login operation
        """
        try:
            request = requests.post(self.ip + '/login.html', 'pw=' + self._passwd, timeout=5)
            status_code = request.status_code
        except:
            status_code = -1
        return status_code

    def _logout(self):
        """
        Logout from Energenie socket
            Returns:
                Status code for logout operation
        """
        try:
            request = requests.post(self.ip + '/login.html')
            status_code = request.status_code
        except:
            status_code = -1
        return status_code

    def _validate_ip(self, ip):
        # TODO check if there is http at the beginning, if there is, remove and check ip, at the end add
        """
        Validate power manager ip address ipv4
            Args:
                ip: ipv4 address of Energenie socket in the LAN
            Returns:
                The return value. If address valid - True, False otherwise
        """
        try:
            host_bytes = ip.split('.')
            valid = [int(b) for b in host_bytes]
            valid = [b for b in valid if (b >= 0) and (b <= 255)]
            return len(host_bytes) == 4 and len(valid) == 4
        except:
            return False

    def _validate_socket(self, socket):
        """
        Validate power manager socket/group name
            Args:
                socket: socket/group (1, 23, 234, 1234, etc).
            Returns:
                The return value. If socket/group valid - True, False otherwise
        """
        try:
            valid = [int(b) for b in socket]
            valid = [b for b in valid if (b >= 1) and (b <= 4)]
            return len(socket) == len(valid)
        except:
            return False

    def _get_details(self, isInit=False):
        """
        Get detailed info about Energenie socket
            Args:
                ip: ipv4 address of Energenie socket in the LAN
            Returns:
                if success set online=True, else online=False
        """
        if isInit:
            try:
                request = requests.post(self.ip + '/lan_settings.html')
                self.ip = 'http://' + str(request.text[3226:3243]).replace('"', '').rstrip()
                self.mac = str(request.text[4383:4395]).rstrip()
                self.dhcp = bool(request.text[3057:3058])
            except:
                self.online = False
        try:
            request = requests.get(self.ip + '/energenie.html')
            txt = request.text
            state_txt = txt[361:368]
            state_txt = state_txt.split(',')
            # print(state_txt)
            self.name = txt[715:747].rstrip()
            self.socket1 = {'name': txt[1721:1732].rstrip(), 'state': int(state_txt[0])}
            self.socket2 = {'name': txt[1763:1774].rstrip(), 'state': int(state_txt[1])}
            self.socket3 = {'name': txt[1805:1816].rstrip(), 'state': int(state_txt[2])}
            self.socket4 = {'name': txt[1847:1858].rstrip(), 'state': int(state_txt[3])}
            self.updated = str(datetime.datetime.now())
            self.online = True
        except:
            self.online = False

    def update(self, isInit=False):
        """
        Update state of Energenie socket, only names, time and states
            Args:
                isInit: default=False, update only main info, otherwise - full info
            Returns:
                if success set online=True, else online=False
        """
        self._logout()
        if self._login() == 200:
            self._get_details(isInit)
        else:
            self.online = False
        self._logout()

    def toggle_pm(self, command='0', socket='1234'):
        """
        Toggle power manager sockets - on, off or revert.
            Args:
                command: '0' - off, '1' - on ('0' - default)
                socket: socket name or group of sockets - '1', '123', '24', '1234', etc, default = '1234'
            Returns:
                if success set online=True, else online=False
        """
        self._logout()
        if (self._login() == 200) and self._validate_socket(socket):
            for i in socket:
                request = requests.post(self.ip, 'cte' + str(i) + '=' + str(command))
        else:
            self.online = False
        self._logout()

    def toJson(self):
        """
        Serialize to the JSON custom object
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


if __name__ == "__main__":
    p1 = Energenie('http://you_energenie_ip', 'you_energenie_pass')
    p1.update(True)
    print(p1.toJson())
