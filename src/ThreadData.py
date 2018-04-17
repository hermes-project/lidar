import sys
from threading import Thread
import time
from rplidar import RPLidar as rp


class ThreadData(Thread):

    def __init__(self, resolution, lidar):
        Thread.__init__(self)
        self.resolution = resolution
        self.lidar = lidar

    def run(self):

        generated_data = [0] * ((360. / self.resolution) * 4.)
        i = 0
        previous_bool = False
        for measure in self.lidar.iter_measures():

            if measure[0] and not previous_bool: # Si True precede d un False
                i = (i+1) % 4
                previous_bool = True
            elif not measure[0] :
                previous_bool = False
            around = self.resolution * 10
            measure[2] = ((round(measure[2]/around, 1)*around) % 360)
            generated_data[self.getIndex(measure[2], i)] = measure[3]

    def getIndex(self, alpha, i):

        index = i * ( 360. / self.resolution) + (alpha / self.resolution)

        return index