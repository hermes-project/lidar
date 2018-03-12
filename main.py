#!/usr/bin/env python3
from time import sleep, time

import lib.rplidar as rplidar
import configparser
from matplotlib import pyplot as plt
from math import cos,sin,pi
from numpy.random import rand, randint

from src.analyze_dic import analyze_dic
from src.data_generator import generator
from src.liaison_objets import laison_objets


#Nombre de tests, pour le calcul de temps moyens
N_TESTS=1


#Recuperationnage de la config:
config = configparser.ConfigParser()
config.read('config.ini')
nombre_tours = float(config['MESURES']['nombre_tours'])
precision = float(config['MESURES']['precision'])
distance_max = int(config['DETECTION']['distance_max'])
distance_infini = int(config['DETECTION']['distance_infini'])
tolerance = int(config['CATEGORISATION']['tolerance'])
seuil = int(config['CATEGORISATION']['seuil'])

#Le lidar:
lidar = rplidar.RPLidar("/dev/ttyUSB0")
lidar.start_motor()
sleep(3) #Laisse le temps au lidar de prendre sa vitesse

tot=0    #Mesure du temps d'execution
for i in range(N_TESTS):
    t=time()
    dico=generator(lidar,nombre_tours,precision)
    lidar.stop()
    limits=analyze_dic(dico,distance_max)
    print(limits)
    laison_objets(limits,tolerance,seuil)
    l=[]
    for a in limits:
        for n in range(len(a)):
            l.append(a[n])
    detectedx=[dico[a]*cos(2*pi-2*pi*a/360.0) for a in l]
    detectedy=[dico[a]*sin(2*pi-2*pi*a/360.0) for a in l]

    x=[d*cos(2*pi-2*pi*a/360.0) for a,d in zip(dico.keys(),dico.values())]
    y=[d*sin(2*pi-2*pi*a/360.0) for a,d in zip(dico.keys(),dico.values())]
    tot+=time()-t

lidar.stop_motor()
tot/=N_TESTS
print(tot)
fig=plt.figure()
ax=fig.add_subplot(111)
ax.set_xlim(-5000,5000)
ax.set_ylim(-5000,5000)
ax.axhline(0,0)
ax.axvline(0,0)
plt.plot(x,y,'ro',markersize=0.6)
plt.plot(detectedx,detectedy,'bo',markersize=1.8)
plt.show()