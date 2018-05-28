#!/usr/bin/env python3
# coding: utf-8
from threading import Thread
import queue
from serial.tools.list_ports import comports
from rplidar import RPLidar as Rp
import configparser
import logging.config

_loggerRoot = logging.getLogger("ppl")

config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")
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
        self.nombre_tours = nombre_tours
        self.running = True
        self.generated_data = []
        self.readyData = queue.Queue(maxsize=10)
        self.ready = False

    def run(self):
        self.generated_data = [[0, False] for _ in range(int((360. / self.resolution) * float(
            self.nombre_tours)))]  # creation de la liste cyclique qui s'actualise tous les tours
        i = 0  # on utilise un booleen pour verifier reinitialiser les valeurs non update sur un tour
        # afin d'eviter de garder des valeurs obselete
        previous_bool = False
        around = self.resolution * 10
        for newTurn, quality, angle, distance in self.lidar.iter_measures():  # on recupere les valeurs du lidar
            if newTurn and not previous_bool:  # Si True precede d un False, on est sur un nouveau tour
                i = int((i + 1) % self.nombre_tours)
                previous_bool = True
                self.readyData = []
                for x in self.generated_data:
                    if x[1]:
                        x[1] = False
                    else:
                        x = [0, False]
                    self.readyData.append(x[0])
                self.ready = True
            elif not newTurn:
                previous_bool = False
            angle = ((round(angle / around, 1) * around) % 360)
            # l'indice dans la liste determine l'angle du lidar, on reduit ainsi la liste.
            self.generated_data[self.get_index(angle, i)] = [distance, True]
            if not self.running:
                break

    def get_index(self, alpha, i):  # methode qui permet de donner l'indice de la liste à partir d'un angle
        index = int(i * (360. / self.resolution) + (alpha / self.resolution))
        return index

    def stop_lidar(self):  # methode pour arreter le LiDAR
        self.running = False
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()

    def is_ready(self):
        if self.ready:
            self.ready = False
            return True
        return False
