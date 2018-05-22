#!/usr/bin/env python3
# coding: utf-8
import socket
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")
server = int(config['COMMUNICATION SOCKET']['server'])
port = int(config['COMMUNICATION SOCKET']['port'])
HL_connected = config['COMMUNICATION SOCKET']['HL_connected'] == "True"


def HL_socket():
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect((server, port))
    print("Connection on {}".format(port))

    return s


def stop_com_HL(socket):
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    print("Close")
    socket.close()
