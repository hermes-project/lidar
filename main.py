#!/usr/bin/env python3
from time import sleep, time

import lib.rplidar as rplidar
import configparser
from matplotlib import pyplot as plt
from matplotlib import animation as anim
from math import cos, sin, pi
from numpy.random import rand, randint
from matplotlib.projections import PolarAxes

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
resolution_degre = float(config['MESURES']['resolution_degre'])
resolution = 0.5*2*pi/360 # en radian
distance_max = int(config['DETECTION']['distance_max'])
distance_infini = int(config['DETECTION']['distance_infini'])
tolerance_predicted_fixe_r = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe_r'])
tolerance_predicted_fixe_theta = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe_theta'])
tolerance_predicted_fixe = [tolerance_predicted_fixe_r,tolerance_predicted_fixe_theta]
tolerance_kalman_r = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_kalman_r'])
tolerance_kalman_theta = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_kalman_theta'])
tolerance_kalman = [tolerance_kalman_r,tolerance_kalman_theta]

try:
        # Le lidar:
        lidar = rplidar.RPLidar("/dev/ttyUSB0")
        lidar.start_motor()
        sleep(3)  # Laisse le temps au lidar de prendre sa vitesse

        tot = 0    # Mesure du temps d'execution
        plt.ion()
        fig = plt.figure()
        # ax = fig.add_subplot(111)
        ax = fig.add_subplot(111, projection='polar')  # polaire !
        #ax.set_xlim(-2000, 2000)
        #ax.set_ylim(-2000, 2000)
        ax.set_xlim(0, +distance_max)
        ax.set_ylim(2*pi)
        ax.axhline(0, 0)
        ax.axvline(0, 0)
        #x = []
        #y = []
        #ax.plot(x, y, 'r')
        r = []
        theta = []
        ax.plot(r, theta, 'r')

        while affichage_continu:
            for i in range(N_TESTS):
                t = time()
                dico = generator(lidar, nombre_tours, resolution_degre)
                print(dico)
                lidar.stop()
                limits = analyze_dic(dico, distance_max)
                print("Ostacles détectés aux angles:", limits)

                list_obstacles = liaison_objets(dico, limits, tolerance_predicted_fixe, tolerance_kalman)

                list_detected = []
                for detected in limits:
                    for n in range(len(detected)):
                        list_detected.append(detected[n])

                ax.clear()
                #ax.set_xlim(-2000, 2000)
                #ax.set_ylim(-2000, 2000)
                #ax.axhline(0, 0)
                #ax.axvline(0, 0)
                ax.set_xlim(0, 2*pi)
                ax.set_ylim(0, +distance_max)
                ax.axhline(0, 0)
                ax.axvline(0, 0)

                for o in list_obstacles:
                    angle = o.center
                    r = dico[angle]
                    print(angle)
                    print(r)
                    #x = r*cos(-angle*2*pi/360)
                    #y = r*sin(-angle*2*pi/360)
                    #circle = plt.Circle((x, y), o.width, color='g')
                    #circle = plt.Circle((500, 700), 200, color='g')
                    #ax.add_artist(circle)
                    colors = 2 * pi * rand(150)
                    c = ax.scatter(angle, r, c='g', s=(o.width)*2, cmap='hsv', alpha=0.75)

                # Listes des positions des obstacles à afficher
                # detectedx = [dico[detected]*cos(2*pi-2*pi*detected/360.0) for detected in list_detected]
                # detectedy = [dico[detected]*sin(2*pi-2*pi*detected/360.0) for detected in list_detected]
                detected_r = [dico[detected] for detected in list_detected]
                detected_theta = [detected for detected in list_detected]

                # Listes des positions des points à afficher
                # x = [d*cos(2*pi-2*pi*a/360.0) for a, d in zip(dico.keys(), dico.values())]
                # y = [d*sin(2*pi-2*pi*a/360.0) for a, d in zip(dico.keys(), dico.values())]
                r = [distance for distance in dico.values()]
                theta = [angle for angle in dico.keys()]

                t = time()-t
                # tot += t  # TODO : tot n'est pas défini !!!

                print("Temps d'execution:", t)

                #plt.plot(x, y, 'ro', markersize=0.6)
                plt.plot(theta, r, 'ro', markersize=0.6)
                #plt.plot(detectedx, detectedy, 'bo', markersize=1.8)
                plt.plot(detected_theta, detected_r, 'bo', markersize=1.8)
                plt.grid()
                fig.canvas.draw()
                lidar.start()

except KeyboardInterrupt:
    lidar.stop_motor()
    lidar.stop()
    lidar.disconnect()
