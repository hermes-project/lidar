#!/usr/bin/env python3
# coding: utf-8
from time import time
from math import pi
from time import time
import socket


def HL_socket():
    """
    Creation d'un socket de communication avec le HL du robot.

    """

    server = "127.0.0.2"
    port = 15550

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect((server, port))
    print("Connection on {}".format(port))

    return s
