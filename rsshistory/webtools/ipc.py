"""
Inter process communication. Communication between scraping/crawl server
"""

import json
import pickle
import socket
import time


DEFAULT_PORT = 5007


def object_to_bytes(input_object):
    return pickle.dumps(input_object, protocol=pickle.HIGHEST_PROTOCOL)


def object_from_bytes(all_bytes):
    return pickle.loads(all_bytes)


def object_to_command(command_string, input_object):
    """
    TODO: All three functions are not currently used
    Pickle uses 0 byte for something.
    I use it signal end of command.

    We could rewrite protocol to support pickle, but that would be a pickle!
    """
    data = object_to_bytes(input_object)
    return bytes_to_command(command_string, data)


def bytes_to_command(command_string, bytes):
    command_string = command_string + ":"

    total = bytearray(command_string.encode())
    total.extend(bytearray(bytes))
    total.extend(bytearray((0).to_bytes(1, byteorder="big")))
    return total


def string_to_command(command_string, string):
    return bytes_to_command(command_string, string.encode())


def commands_from_bytes(read_message):
    """
    returns vector of [command, data]
    """
    result = []

    index = 0
    while True:
        command, data, read_message = get_command_and_data(read_message)
        if not command:
            break

        result.append([command, data])

    return result


def get_command_and_data(read_message):
    command, remaining = get_command_bytes(read_message)

    if not command:
        return [None, None, None]

    wh = command.find(b"\x3A")
    if not wh:
        print("Cannot find ':' in response")
        return [None, None, None]

    else:
        command_string = command[:wh].decode()
        data = command[wh + 1 :]
        return [command_string, data, remaining]


def get_command_bytes(read_message):
    wh = read_message.find(b"\x00")

    if wh >= 0:
        command = read_message[:wh]
        read_message = read_message[wh + 1 :]

        return [command, read_message]

    return [None, None]


class SocketConnection(object):
    def __init__(self, conn=None):
        self.conn = conn
        self.read_message = bytearray()
        self.closed = False

    def gethostname():
        return socket.gethostname()

    def connect(self, host, port):
        if host:
            self.host = host
        else:
            self.host = SocketConnection.gethostname()

        if port:
            self.port = port
        else:
            self.port = DEFAULT_PORT

        self.conn = socket.socket()
        self.conn.settimeout(1.0)  # to be able to make ctrl-c

        try:
            self.conn.connect((self.host, self.port))
            return True

        except Exception as E:
            self.closed = True
            return False

    def send(self, bytes):
        if self.is_closed():
            return False

        try:
            self.conn.sendall(bytes)
            return True
        except Exception as E:
            self.closed = True
            return False

    def send_command_bytes(self, command_string, bytes):
        bytes = bytes_to_command(command_string, bytes)
        self.send(bytes)

    def send_command_string(self, command_string, string):
        bytes = string_to_command(command_string, string)
        self.send(bytes)

    def get_command_bytes(self):
        while True:
            wh = self.read_message.find(b"\x00")

            if wh >= 0:
                command = self.read_message[:wh]
                self.read_message = self.read_message[wh + 1 :]

                return command

            if self.is_closed():
                return

            bytes = None
            try:
                if self.is_data():
                    bytes = self.conn.recv(1024)
                else:
                    time.sleep(1)

            except socket.timeout:
                return

            except Exception as E:
                self.closed = True
                return

            if not bytes:
                return

            if len(bytes) == 0:
                return

            if bytes:
                self.read_message.extend(bytearray(bytes))

            wh = self.read_message.find(b"\x00")

            if wh >= 0:
                command = self.read_message[:wh]
                self.read_message = self.read_message[wh + 1 :]

                return command

    def get_command_and_data(self):
        command = self.get_command_bytes()

        if not command:
            return

        wh = command.find(b"\x3A")
        if not wh:
            print("Cannot find ':' in response")
            return

        else:
            command_string = command[:wh].decode()
            data = command[wh + 1 :]
            return [command_string, data]

    def close(self):
        if not self.is_closed():
            try:
                self.conn.close()
            except Exception as E:
                pass

            self.closed = True

    def is_data(self):
        try:
            bytes = self.conn.recv(1024, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if bytes:
                return len(bytes) > 0
            else:
                return False
        except Exception as E:
            return False

    def is_closed(self):
        return self.closed

    def __str__(self):
        return "{} {}".format(self.conn, self.closed)
