#!/usr/bin/env python3
from matplotlib import pyplot as plt
from math import sin, cos, pi

from rplidar import RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)
info = lidar.get_info()
print(info)
health = lidar.get_health()
print(health)

plt.ion()
fig=plt.figure()
ax=fig.add_subplot(111)
x=[]
y=[]
ax.plot(x,y,'r.')

r=[]
theta=[]
try:
    print('Demmarage des mesures...')
    for i, scan in enumerate(lidar.iter_scans(scan_type='express')):
        for mesure in scan:
            theta.append(mesure[1])
            r.append(mesure[2])
        lidar.clean_input()

        x=[ri*cos(2*pi*ti/360) for ri, ti in zip(r,theta)]
        y=[ri*sin(2*pi*ti/360) for ri, ti in zip(r,theta)]
        ax.clear()
        ax.plot(x,y,'r.')
        plt.ylim([-6000, 6000])
        plt.xlim([-6000, 6000])
        plt.grid()
        fig.canvas.draw()
        if(len(theta)>400):
            theta.clear()
            r.clear()
        print("Scan N° %d termine" % i)
        if i > 200:
            break

except KeyboardInterrupt:
    print("Arret des scans")

lidar.stop()
lidar.stop_motor()
lidar.disconnect()



# theta=[]
# r=[]
# for line in infile:
#     data=line.split(';')[1:3]
#     theta.append(float(data[1]))
#     r.append(float(data[0]))
#
# x=[ri*cos(2*pi*ti/360) for ri, ti in zip(r,theta)]
# y=[ri*sin(2*pi*ti/360) for ri, ti in zip(r,theta)]
# print(x)
# print(y)
#
#
# plt.plot(x,y,'ro')
# plt.show()