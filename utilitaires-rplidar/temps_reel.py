"""
Script d'affichage des mesures du LiDAR en temps réel
"""

from math import sin, cos, pi

from matplotlib import pyplot as plt

from rplidar import RPLidar

import logging.config

_logger = logging.getLogger("ppl")
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)
info = lidar.get_info()
_logger.debug("Info: %s.", info)
health = lidar.get_health()
_logger.debug("Health: %s.", health)

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
x = []
y = []
ax.plot(x, y, 'r.')

r = []
theta = []
try:
    _logger.info('Demmarage des mesures...')
    for i, scan in enumerate(lidar.iter_scans(max_buf_meas=10000)):
        print(scan)
        for mesure in scan:
            theta.append(mesure[1])
            r.append(mesure[2])
        lidar.clean_input()

        x = [ri*cos(2*pi*ti/360) for ri, ti in zip(r, theta)]
        y = [ri*sin(2*pi*ti/360) for ri, ti in zip(r, theta)]
        ax.clear()
        ax.plot(x, y, 'ro', markersize=0.35)
        plt.ylim([-6000, 6000])
        plt.xlim([-6000, 6000])
        plt.grid()
        fig.canvas.draw()
        if len(theta) > 400:
            theta.clear()
            r.clear()
        _logger.info("Scan N° %s termine.", i)
        if i > 1000:
            break
except KeyboardInterrupt:
    _logger.info("Arret des scans.")
