#!/usr/bin/env python3
import logging.config
from csv import writer
from os import mkdir
from os.path import isdir
from time import sleep, time

from src.HL_connection import hl_connected
from src.HL_connection import hl_socket
from src.HL_connection import stop_com_hl
from src.ThreadData import ThreadData
from src.affichage import afficher_en_polaire, affichage, affichage_cartesien, affichage_polaire, \
    init_affichage_cartesien, init_affichage_polaire
from src.mesures import compute_measures

if not isdir("./Logs/"):
    mkdir("./Logs/")


logging.config.fileConfig('./configs/config_log.ini')
_loggerPpl = logging.getLogger("ppl")
_loggerHl = logging.getLogger("hl")
data_file = open("Logs/RawData.logs", "a")
data_writer = writer(data_file, delimiter=" ")
data_writer.writerow(["#NEW"])
socket = None
thread_data = None
ax = None
fig = None
message = None


try:
    # Liste des positions des anciens obstacles
    previous_obstacles = []

    # Creation de socket pour communiquer avec le HL
    if hl_connected:
        socket = hl_socket()

    # Demarre le Thread recevant les donnees
    thread_data = ThreadData()
    thread_data.start()

    # Attente de quelques tours pour que le lidar prenne sa pleine vitesse et envoie assez de points
    sleep(1)

    # Initialisation de l'affichage
    if not hl_connected and affichage:
        print("Affichage init")
        if afficher_en_polaire:
            ax, fig = init_affichage_polaire()
        else:
            ax, fig = init_affichage_cartesien()

    # Initialisation des valeurs pour le calcul du temps d'exécution
    t = time()
    te = t

    # Boucle de récupération,de traitement des données, d'envoi et d'affichage
    while True:
        # Aucun interet à spammer, on a moins de chance de bloquer l'execution du thread temporairement

        # Calcul du temps d'exécution : aussi utilisé pour le Kalman
        te = (time() - t)
        t = time()
        # On récupère les données du scan du LiDAR et on fait les traitements
        measures, limits, obstacles, previous_obstacles = compute_measures(te, previous_obstacles, thread_data)
        # Envoi de la position du centre de l'obstacle détécté pour traitement par le pathfinding

        sent_list = []
        for o in obstacles:
            angle = o.center
            r = measures[angle]
            sent_list.append(str((r, angle)))
            message = ";".join(sent_list)
            message = message + "\n"
        _loggerHl.debug("envoi au hl: %s.", message)
        data_writer.writerow(measures.values())
        if hl_connected:
            socket.send(message.encode('ascii'))
        thread_data.lidar.clean_input()
        # Affichage des obstacles, de la position Kalman, et des points détectés dans chaque obstacle
        if affichage:
            if afficher_en_polaire:
                affichage_polaire(limits, ax, obstacles, measures, fig)
            else:
                affichage_cartesien(limits, ax, obstacles, measures, fig)

except KeyboardInterrupt:
    # Arrêt du système
    if hl_connected and socket:
        stop_com_hl(socket)
    _loggerPpl.info("ARRET DEMANDE.")
    if thread_data:
        thread_data.stop_lidar()
        thread_data.join()
        thread_data = None

finally:
    # Arrêt du système
    if hl_connected and socket:
        stop_com_hl(socket)
    if thread_data:
        thread_data.stop_lidar()
        thread_data.join()
        thread_data = None
    data_file.close()

