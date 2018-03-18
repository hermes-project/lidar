#!/usr/bin/env python3
from time import sleep, time

import lib.rplidar as rplidar
import configparser
from matplotlib import pyplot as plt
from matplotlib import animation as anim
from math import cos, sin, pi
from numpy.random import rand, randint

from src.analyze_dic import analyze_dic
from src.data_generator import generator
from src.liaison_objets import liaison_objets

# Nombre de tests, pour le calcul de temps moyens
N_TESTS = 1
affichage_continu = True


# Recuperationnage de la config
config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")
nombre_tours = float(config['MESURES']['nombre_tours'])
precision = float(config['MESURES']['precision'])
distance_max = int(config['DETECTION']['distance_max'])
distance_infini = int(config['DETECTION']['distance_infini'])
tolerance_predicted_fixe = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe'])
tolerance_Kalman = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_Kalman'])

try:
        # Le lidar:
        lidar = rplidar.RPLidar("/dev/ttyUSB0")
        lidar.start_motor()
        sleep(3) # Laisse le temps au lidar de prendre sa vitesse

        tot = 0    # Mesure du temps d'execution
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(-2000, 2000)
        ax.set_ylim(-2000, 2000)
        ax.axhline(0, 0)
        ax.axvline(0, 0)
        x = []
        y = []
        ax.plot(x,y,'r')

        while affichage_continu:
            for i in range(N_TESTS):
                t = time()
                dico = generator(lidar, nombre_tours, precision)
                print(dico)
                lidar.stop()
                limits = analyze_dic(dico, distance_max)
                print("Ostacles détectés aux angles:", limits)

                list_obstacles = liaison_objets(dico,limits,tolerance_predicted_fixe,tolerance_Kalman)

                l = []
                for a in limits:
                    for n in range(len(a)):
                        l.append(a[n])
                ax.clear()
                ax.set_xlim(-2000, 2000)
                ax.set_ylim(-2000, 2000)
                ax.axhline(0, 0)
                ax.axvline(0, 0)

                for o in list_obstacles:
                    angle = o.center
                    r = dico[angle]
                    print(angle)
                    print(r)
                    x = r*cos(-angle*2*pi/360)
                    y = r*sin(-angle*2*pi/360)
                    circle = plt.Circle((x,y),o.width,color='g')
                    ax.add_artist( circle )

                # Listes des positions des obstacles à afficher
                detectedx = [dico[a]*cos(2*pi-2*pi*a/360.0) for a in l]
                detectedy = [dico[a]*sin(2*pi-2*pi*a/360.0) for a in l]

                # Listes des positions des points à afficher
                x = [d*cos(2*pi-2*pi*a/360.0) for a,d in zip(dico.keys(),dico.values())]
                y = [d*sin(2*pi-2*pi*a/360.0) for a,d in zip(dico.keys(),dico.values())]
                t = time()-t
                # tot += t  # TODO : tot n'est pas défini !!!

                print("Temps d'execution:",t)

                plt.plot(x, y, 'ro', markersize=0.6)
                plt.plot(detectedx, detectedy, 'bo', markersize=1.8)
                plt.grid()
                fig.canvas.draw()
                lidar.start()

except KeyboardInterrupt:
    lidar.stop_motor()
    lidar.stop()
    lidar.disconnect()
