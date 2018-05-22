#!/usr/bin/env python3
# coding: utf-8
from time import time
from math import pi
from time import time
import socket


def HL_socket(server, port):
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
