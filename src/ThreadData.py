import sys
from threading import Thread
from time import time

from pip import logger
from rplidar import RPLidar as rp


class ThreadData(Thread):

    def __init__(self, resolution, nombre_tours):
        Thread.__init__(self)
        self.lidar = rp("/dev/ttyUSB0", baudrate=115200)
        self.lidar.start_motor()
        self.lidar.start()

        self.resolution = resolution
        self.nombre_tours = nombre_tours
        self.running = True
        self.generated_data = []
        self.ready = False

    def run(self):
        self.generated_data = [0] * int(((360. / self.resolution) * float(self.nombre_tours)))
        i = 0
        previous_bool = False
        for newTurn, quality, angle, distance in self.lidar.iter_measures():
            if newTurn and not previous_bool:  # Si True precede d un False
                i = int((i + 1) % self.nombre_tours)
                previous_bool = True
                self.ready=True
                for x in self.generated_data:
                    if x[1]:
                        x[1] = False
                    else:
                        x = [0, False]
            elif not newTurn:
                previous_bool = False
            around = self.resolution * 10
            angle = ((round(angle / around, 1) * around) % 360)
            self.generated_data[self.getIndex(angle, i)] = [distance, True]
            if not self.running:
                break

    def getIndex(self, alpha, i):

        index = int(i * (360. / self.resolution) + (alpha / self.resolution))

        return index

    def stopLidar(self):
        print("STOP")
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()
        self.running = False
