#!/usr/bin/env python3
# coding: utf-8
import configparser
import logging.config
import queue
from threading import Thread
from time import time

from serial.tools.list_ports import comports

from libs.rplidar import RPLidar as Rp

_loggerRoot = logging.getLogger("ppl")

config = configparser.ConfigParser()
config.read('./configs/config.ini', encoding="utf-8")
resolution_degre = float(config['MESURES']['resolution_degre'])
nombre_tours = float(config['MESURES']['nombre_tours'])


class ThreadData(Thread):

    def __init__(self):  # initialisation du LiDAR.
        _loggerRoot.info("Lancement thread de recuperation des donnees.")
        Thread.__init__(self)
        try:
            self.lidar = Rp(comports()[0].device)  # Tente de se connecter au premier port Serie disponible
        except IndexError:
            _loggerRoot.error("Pas de connexion serie disponible.")
            exit()
        self.lidar.start_motor()
        self.lidar.start()
        self.resolution = resolution_degre
        self.running = True
        self.generated_data = []
        self.readyData = queue.Queue()

    def run(self):
        # Liste contenant les donnees d'un scan entier = un tour
        i = 0  # on utilise un booleen pour verifier reinitialiser les valeurs non update sur un tour
        # afin d'eviter de garder des valeurs obselete
        around = self.resolution * 10
        for scans in self.lidar.iter_scans(max_buf_meas=4095):
            self.generated_data = [0 for _ in range(int((360. / self.resolution)))]
            for _, angle, distance in scans:
                angle = ((round(angle / around, 1) * around) % 360)
                self.generated_data[self.get_index(angle)] = distance
            self.readyData.put(self.generated_data.copy())
            if not self.running:
                break

    def get_index(self, alpha):  # methode qui permet de donner l'indice de la liste à partir d'un angle
        index = int(alpha / self.resolution)
        return index

    def stop_lidar(self):  # methode pour arreter le LiDAR
        self.running = False
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()
