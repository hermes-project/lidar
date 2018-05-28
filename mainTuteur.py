#!/usr/bin/env python3
from time import sleep, time
import configparser
from math import cos, sin, pi
import pylab as pl
from os.path import isfile

from src.analyze_dic import analyze_dic
from src.data_cleaner import data_cleaner
from src.liaison_objets import liaison_objets
from src.file_data_manager import readData, cleanData
pl.switch_backend('TkAgg')

# Recuperationnage de la config
config = configparser.ConfigParser()
config.read('./configs/config.ini', encoding="utf-8")
nombre_tours = float(config['MESURES']['nombre_tours'])
resolution_degre = float(config['MESURES']['resolution_degre'])
resolution = 0.5 * 2 * pi / 360  # en radian
distance_max = int(config['DETECTION']['distance_max'])
distance_infini = int(config['DETECTION']['distance_infini'])
ecart_min_inter_objet = int(config['DETECTION']['ecart_min_inter_objet'])
tolerance_predicted_fixe_r = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe_r'])
tolerance_predicted_fixe_theta = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe_theta'])
tolerance_predicted_fixe = [tolerance_predicted_fixe_r, tolerance_predicted_fixe_theta]
tolerance_kalman_r = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_kalman_r'])
tolerance_kalman_theta = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_kalman_theta'])
tolerance_kalman = [tolerance_kalman_r, tolerance_kalman_theta]
seuil_association = int(config['OBSTACLES FIXES OU MOBILES']['seuil_association'])

data = []

if isfile("src/scanData.csv"):
    print("FICHIER DE DONNEES TROUVE")
    data = cleanData(readData("src/scanData.csv"), resolution_degre, nombre_tours)
else:
    print("ERREUR: FICHIER DE DONNEES NON TROUVE")
    exit()

pl.ion()
fig = pl.figure()
ax = fig.add_subplot(111, polar=True)  # polaire !
ax.set_xlim(0, 3 * distance_max)
ax.set_ylim(2 * pi)
ax.axhline(0, 0)
ax.axvline(0, 0)
r = []
theta = []
ax.scatter(theta, r)

# print(data)
try:
    last_time = time()
    list_obstacles_precedente = []  # Liste des positions des anciens obstacles
    for i in range(len(data)):
        currentData = data[i]
        Te = (time() - last_time) * 8.
        last_time = time()
        # A ~10Hz, pour coller aux mesures du LiDAR
        sleep(0.1)

        # Mise en forme des donnees, avec un dictionnaire liant angles a la distance associee, et moyennant les
        # distances si il y a plusieurs tours effectues
        dico = data_cleaner(currentData, nombre_tours)
        # Detection des bords d'obstacles
        limits = analyze_dic(dico, distance_max, ecart_min_inter_objet)
        # Mise a jour des obstacles detectes, incluant le filtre de kalman
        list_obstacles, list_obstacles_precedente = liaison_objets(dico, limits, seuil_association,
                                                                   Te, list_obstacles_precedente)

        list_detected = []
        for detected in limits:
            print(detected)
            for n in range(len(detected)):
                list_detected.append(detected[n])

        ax.clear()
        ax.set_xlim(0, 2 * pi)
        ax.set_ylim(0, +distance_max)
        ax.axhline(0, 0)
        ax.axvline(0, 0)

        for o in list_obstacles:
            angle = o.center
            r = dico[angle]
            circle = pl.Circle((r * cos(angle), r * sin(angle)), o.width / 2, transform=ax.transData._b, color='g',
                               alpha=0.4)
            ax.add_artist(circle)

            if o.get_predicted_kalman() is not None:
                x_kalman = o.get_predicted_kalman()[0][0]
                y_kalman = o.get_predicted_kalman()[0][2]
                circle = pl.Circle((x_kalman, y_kalman), o.width / 2, transform=ax.transData._b,
                                   color='b',
                                   alpha=0.4)
                ax.add_artist(circle)
        # Listes des positions des obstacles à afficher
        detected_r = [dico[detected] for detected in list_detected]
        detected_theta = [detected for detected in list_detected]
        # Listes des positions des points à afficher
        r = [distance for distance in dico.values()]
        theta = [angle for angle in dico.keys()]
        pl.plot(theta, r, 'ro', markersize=0.6)
        pl.plot(detected_theta, detected_r, 'bo', markersize=1.8)
        pl.grid()
        fig.canvas.draw()

except KeyboardInterrupt:
    print("ARRET DEMANDE")
    pl.close()
