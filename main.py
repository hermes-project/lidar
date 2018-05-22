#!/usr/bin/env python3
from time import sleep, time

from src.HL_connection import hl_connected
from src.HL_connection import hl_socket
from src.HL_connection import stop_com_hl
from src.ThreadData import ThreadData
from src.affichage import *
from src.mesures import mesures

socket = None
thread_data = None
ax = None
fig = None

try:

    # Liste des positions des anciens obstacles
    list_obstacles_precedente = []

    # Creation de socket pour communiquer avec le HL
    if hl_connected:
        socket = hl_socket()

    # Demarre le Thread recevant les donnees
    thread_data = ThreadData()
    thread_data.start()

    # Attente de quelques tours pour que le lidar prenne sa pleine vitesse et envoie assez de points
    sleep(2)

    # Initialisation de l'affichage
    if not hl_connected:
        ax, fig = init_affichage_cartesien()

    # Initialisation des valeurs pour le calcul du temps d'exécution
    t = time()
    te = t

    # Boucle de récupération,de traitement des données, d'envoi et d'affichage
    while True:

        # Attendre qu'au moins 1 scan soit effectué
        sleep(0.05)
        if not thread_data.is_ready():
            continue

        # Calcul du temps d'exécution : aussi utilisé pour le Kalman
        te = (time() - t)
        t = time()

        # On récupère les données du scan du LiDAR et on fait les traitements
        dico, limits, list_obstacles, list_obstacles_precedente = mesures(te, list_obstacles_precedente, thread_data)

        # Envoi de la position du centre de l'obstacle détécté pour traitement par le pathfinding
        if hl_connected:
            for o in list_obstacles:
                angle = o.center
                r = dico[angle]
                socket.send([r, angle])

        # Affichage des obstacles, de la position Kalman, et des points détectés dans chaque obstacle
        else:
            affichage_cartesien(limits, ax, list_obstacles, dico, fig)

        # Affichage du temps d'exécution
        print("Temps d'execution:", t)

except KeyboardInterrupt:
    # Arrêt du système
    if hl_connected:
        stop_com_hl(socket)
    print("ARRET DEMANDE")
    if thread_data:
        thread_data.stop_lidar()
        thread_data.join()

finally:
    # Arrêt du système
    if hl_connected:
        stop_com_hl(socket)
    print("ARRET DEMANDE")
    if thread_data:
        thread_data.stop_lidar()
        thread_data.join()
