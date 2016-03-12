from socketIO_client import SocketIO, BaseNamespace

class MainNamespace(BaseNamespace):

    def on_msg(self, *args):
        print('on_message', args)

    def on_connect(self):
        print('[Connected]')

    def on_disconnect(self):
        print('[DisConnected]')

    def on_relay(self, *args):
    	message = args[0]
    	self.emit('relay', {'relay': message['relay']})

socketIO = SocketIO('http://localhost', 8000)
main_namespace = socketIO.define(MainNamespace, '/socket_rpi')
socketIO.wait(seconds=2)