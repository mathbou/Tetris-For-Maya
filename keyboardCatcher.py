import socket
from threading import Thread
from pynput import keyboard
from tetrisGlobals import *

class KeyLogger(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.action = 0

    def reset_action(self):
        self.action = 0

    def on_press(self, key):
        try:
            key_value = key.char
        except AttributeError:
            key_value = key
        finally:
            if key_value == keyboard.Key.up:
                self.action = ROTATE
            elif key_value == keyboard.Key.down:
                self.action = SOFTD
            elif key_value == keyboard.Key.left:
                self.action = LEFT
            elif key_value == keyboard.Key.right:
                self.action = RIGHT
            elif key_value == "c":
                self.action = HOLD
            elif key_value == keyboard.Key.space:
                self.action = HARDD

    def on_release(self, key):
        print('{0} released'.format(key))

        if key == keyboard.Key.end:
            # Stop listener
            return False

    def close(self):
        print "Stopping keyboard catcher"
        self.human_press(keyboard.Key.end)

    @staticmethod
    def human_press(key):
        keyboard.Controller().press(key)
        keyboard.Controller().release(key)

    def run(self):
        # Collect events until released
        print "keyboard catcher running"

        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


def socket_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except socket.error:
            print "socket error"
    return wrapper


class Server(object):

    def __init__(self, keylogger, host="localhost", port=42198):
        self.host = host
        self.port = port
        self.server = None
        self.client = None
        self.keylogger = keylogger

    def run(self):
        # start server
        print "Start server {0}:{1}".format(self.host, self.port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))

        self._listening()

    def _listening(self):
        print "Start listening"

        while True:
            self.server.listen(5)
            self.accept_connection()

            while True:
                packet = self.client.recv(256)
                if packet == GET:
                    self.client.send(str(self.keylogger.action))
                    self.keylogger.reset_action()
                elif packet == KILL:
                    self.kill_server()
                    return False

    @socket_error
    def accept_connection(self):
        self.client, address = self.server.accept()
        print self.client, address

    def kill_server(self):
        self.keylogger.close()

        print "Stopping Server"
        self.client.close()
        self.server.close()


if __name__ == '__main__':
    GET = "get"
    KILL = "kill"

    keylogger = KeyLogger()
    keylogger.start()

    server = Server(keylogger)
    server.run()
