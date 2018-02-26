import csv
from numpy import var
from rplidar import RPLidar
from time import sleep, time
import matplotlib.pyplot as plt
from os import path,makedirs
plt.xkcd()

PORT_NAME = "/dev/ttyUSB0"
ANGLE_INF = 267
ANGLE_SUP = 273
INIT_SPEED = 200  # PWM initial
INCREMENT_SPEED = 82  # on incrementera 10 fois pour arriver a 1020 MAX = 1023
MAX_SPEED = 1023 #VItesse max
SPEED = INIT_SPEED

#Crée le dossier MesureTourResultats si il n'existe pas déjà
if not path.exists("MesureTourResultats"):
    makedirs("MesureTourResultats")
if not path.exists("MesureTourResultats/csv"):
    makedirs("MesureTourResultats/csv")

"""
Test du nombre de mesures moyen par tour pour chaque vitesse, qui permettra d'obtenir une relation potentielle entre la vitesse du moteur(ie la fréquence de scans) et la vitesse du laser(la fréquence de mesures)
Cela devrait permettre d'avoir plus d'infos pour choisir notre vitesse de fonctionnement optimale
"""

lidar = RPLidar(PORT_NAME)
info = lidar.get_info()  # info general sur le lidar
print(info)
health = lidar.get_health()
print(health)

for i in range(round((MAX_SPEED-INIT_SPEED)/INCREMENT_SPEED)):
    print("Mesure",i)
    with open("MesureTourResultats/csv/mesure_"+str(SPEED)+".csv","w") as outfile:
        print("Mesure à un PWM de",SPEED)
        lidar.start_motor()
        lidar._motor_speed=SPEED
        for j, scan in enumerate(lidar.iter_scans()):

