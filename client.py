from threading import Thread
from socketIO_client import SocketIO, BaseNamespace
import RPi.GPIO as GPIO
import os
import time
import serial
import json
import requests
import picamera
from fractions import Fraction
from random import randint

camera = picamera.PiCamera()
camera.vflip = True
camera.iso = 0

URL_SITE = 'http://ojixzzz.science'
pin_relay_1 = 18
pin_relay_2 = 17 
pin_relay_3 = 27
pin_relay_4 = 22
pin_pir = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_pir, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(pin_relay_1, GPIO.OUT)
GPIO.setup(pin_relay_2, GPIO.OUT)
GPIO.setup(pin_relay_3, GPIO.OUT)
GPIO.setup(pin_relay_4, GPIO.OUT)
GPIO.output(pin_relay_1, True)
GPIO.output(pin_relay_2, True)
GPIO.output(pin_relay_3, True)
GPIO.output(pin_relay_4, True)

arduino_ser = serial.Serial(
	port='/dev/ttyAMA0',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)

class MainNamespace(BaseNamespace):

    t = None
    def on_msg(self, *args):
        print('on_message', args)

    def on_connect(self):
        t = Thread(target=self.arduino_thread)
        t.start()
        print('[Connected]')

    def on_disconnect(self):
        t.stop()
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

    def arduino_thread(self):
        lastTemp = 0
        previous_state = False
        current_state = False
        gambar_count = 1
        while 1:
            x=arduino_ser.readline()
            if x:
                try:
                    datajson = json.loads(x)
                except Exception as e:
                    datajson = {'x': 0}
                data = datajson.get('data')
                if data:
                    tempNow = data.get('temp')
                    if tempNow!=lastTemp:
                        datas = {
                            'temp': tempNow,
                        }
                        self.emit('sensor_data', datas)
                    lastTemp = tempNow
            
            previous_state = current_state
            current_state = GPIO.input(pin_pir)
            if current_state != previous_state:
                if current_state:
                    if gambar_count > 9:
                        gambar_count = 1
                    filerand = 'gambar%s.jpg' % gambar_count
                    camera.capture(filerand)
                    filep = open(filerand, 'rb')
                    url = '%s:4855/upload_image' % URL_SITE
                    r_req = requests.post(url, files={'file': filep})
                    filep.close()
                    os.remove(filerand)
                    gambar+=1
            time.sleep(1)

socketIO = SocketIO(URL_SITE, 4855)
main_namespace = socketIO.define(MainNamespace, '/socket_rpi')
socketIO.wait(seconds=5)
