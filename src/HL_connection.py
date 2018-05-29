#!/usr/bin/env python3
# coding: utf-8
import socket
import configparser
from time import sleep
import logging.config

config = configparser.ConfigParser()
config.read('./configs/config.ini', encoding="utf-8")
server = config['COMMUNICATION SOCKET']['server']
port = int(config['COMMUNICATION SOCKET']['port'])
hl_connected = config['COMMUNICATION SOCKET']['hl_connected'] == "True"
_loggerHl = logging.getLogger("hl")


def hl_socket():
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sleep(2)
    s.connect((server, port))
    _loggerHl.info("Connexion sur port %s et server %s.", port, server)

    return s


def stop_com_hl(my_socket):
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    my_socket.close()
    _loggerHl.info("Close socket.")
