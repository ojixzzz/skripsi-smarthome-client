from threading import Thread
from socketIO_client import SocketIO, BaseNamespace
import RPi.GPIO as GPIO
import time
import serial
import json

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
        while 1:
            x=arduino_ser.readline()
            if x:
                datajson = json.loads(x)
                data = datajson.get('data')
                if data:
                    datas = {
                        'temp': data.get('temp'),
                    }
                    self.emit('sensor_data', datas)
            time.sleep(3)

socketIO = SocketIO('http://ojixzzz.science', 4855)
main_namespace = socketIO.define(MainNamespace, '/socket_rpi')
socketIO.wait()
