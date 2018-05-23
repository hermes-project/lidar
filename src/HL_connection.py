#!/usr/bin/env python3
# coding: utf-8
import socket
import configparser
from time import sleep

config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")
server = config['COMMUNICATION SOCKET']['server']
port = int(config['COMMUNICATION SOCKET']['port'])
hl_connected = config['COMMUNICATION SOCKET']['hl_connected'] == "True"


def hl_socket():
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    print("port: ", port, " et server: ", server)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("ah!")
    print("wants to connect")
    sleep(4)
    s.connect((server, port))
    print("Connection on {}".format(port))

    return s


def stop_com_hl(my_socket):
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    print("Close")
    my_socket.close()
