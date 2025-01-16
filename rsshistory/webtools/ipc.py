"""
Inter process communication. Communication between scraping/crawl server
"""

import json
import pickle
import socket
import time


DEFAULT_PORT = 5007


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

    def __del__(self):
        self.close()

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
            return False

    def close(self):
        if not self.is_closed():
            try:
                self.conn.close()
            except Exception as E:
                pass

            self.closed = True

    def is_closed(self):
        return self.closed

    def __str__(self):
        return "{} {}".format(self.conn, self.closed)
