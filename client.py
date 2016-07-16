from socketIO_client import SocketIO, BaseNamespace
import RPi.GPIO as GPIO

import os
import time
import serial
import json
import requests

URL_SITE = 'http://ojixzzz.science'
pin_relay_1 = 18
pin_relay_2 = 17 
pin_relay_3 = 27
pin_relay_4 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_relay_1, GPIO.OUT)
GPIO.setup(pin_relay_2, GPIO.OUT)
GPIO.setup(pin_relay_3, GPIO.OUT)
GPIO.setup(pin_relay_4, GPIO.OUT)
GPIO.output(pin_relay_1, True)
GPIO.output(pin_relay_2, True)
GPIO.output(pin_relay_3, True)
GPIO.output(pin_relay_4, True)

class MainNamespace(BaseNamespace):

    def on_msg(self, *args):
        print('on_message', args)

    def on_connect(self):
        print('[Connected]')

    def on_disconnect(self):
        print('[DisConnected]')

    def on_relay(self, *args):
        message = args[0]
        relay = message.get('relay')
        if relay==1:
            GPIO.output(pin_relay_1, not GPIO.input(pin_relay_1))
        elif relay==2:
            GPIO.output(pin_relay_2, not GPIO.input(pin_relay_2))
        elif relay==3:
            GPIO.output(pin_relay_3, not GPIO.input(pin_relay_3))
        elif relay==4:
            GPIO.output(pin_relay_4, not GPIO.input(pin_relay_4))

        self.emit('relay', {'relay': message['relay']})

    def on_relay_data(self, *args):
        data = {
            'relay_1': GPIO.input(pin_relay_1),
            'relay_2': GPIO.input(pin_relay_2),
            'relay_3': GPIO.input(pin_relay_3),
            'relay_4': GPIO.input(pin_relay_4),
        }
        self.emit('relay_data', data)

socketIO = SocketIO(URL_SITE, 4855)
main_namespace = socketIO.define(MainNamespace, '/socket_rpi')
socketIO.wait()
