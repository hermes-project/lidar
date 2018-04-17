import sys
from threading import Thread
from time import time

from pip import logger
from rplidar import RPLidar as rp


class ThreadData(Thread):

    def __init__(self, resolution, nombre_tours):
        Thread.__init__(self)
        self.lidar = rp("/dev/ttyUSB0")
        self.lidar.start_motor()
        self.lidar.start()

        self.resolution = resolution
        self.nombre_tours = nombre_tours
        self.running = True
        self.generated_data = []
        self.ready = False
        self.readyData=[]

    def run(self):
        self.generated_data = [[0,False] for _ in range(int((360. / self.resolution) * float(self.nombre_tours)))]
        i = 0
        previous_bool = False
        around = self.resolution * 10
        for newTurn, quality, angle, distance in self.lidar.iter_measures():
            if newTurn and not previous_bool:  # Si True precede d un False
                i = int((i + 1) % self.nombre_tours)
                previous_bool = True
                self.readyData=[]
                for x in self.generated_data:
                    if x[1]:
                        x[1] = False
                    else:
                        x = [0, False]
                    self.readyData.append(x[0])
                self.ready=True
            elif not newTurn:
                previous_bool = False
            angle = ((round(angle / around, 1) * around) % 360)
            self.generated_data[self.getIndex(angle, i)] = [distance, True]
            if not self.running:
                break

    def getIndex(self, alpha, i):

        index = int(i * (360. / self.resolution) + (alpha / self.resolution))

        return index

    def stopLidar(self):
        print("STOP LIDAR")
        try:
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()
        except:
            print("ERREUR DANS STOPPING")
        self.running = False
