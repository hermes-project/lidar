#!/usr/bin/env python3
from libs.logging import config, getLogger
from csv import writer
from os import mkdir
from os.path import isdir
from time import sleep

from libs.serial import *
from src.HL_connection import hl_connected
from src.HL_connection import hl_socket
from src.HL_connection import stop_com_hl
from src.ThreadData import ThreadData
from src.mesures import compute_measures

if not isdir("./Logs/"):
    mkdir("./Logs/")


config.fileConfig('./configs/config_log.ini')
_loggerPpl = getLogger("ppl")
_loggerHl = getLogger("hl")
data_file = open("Logs/RawData.logs", "a")
data_writer = writer(data_file, delimiter=" ")
data_writer.writerow(["#NEW"])
socket = None
thread_data = None
ax = None
fig = None
envoi = None


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
    sleep(1)

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
        dico, limits, list_obstacles, list_obstacles_precedente = compute_measures(te, list_obstacles_precedente, thread_data)
        # Envoi de la position du centre de l'obstacle détécté pour traitement par le pathfinding

        liste_envoyee = []
        for o in list_obstacles:
            angle = o.center
            r = dico[angle]
            liste_envoyee.append(str((r, angle)))
            envoi = ";".join(liste_envoyee)
            envoi = envoi + "\n"
        _loggerHl.debug("envoi au hl: %s.", envoi)
        data_writer.writerow(dico.values())
        if hl_connected:
            socket.send(envoi.encode('ascii'))
        thread_data.lidar.clean_input()

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

