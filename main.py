#!/usr/bin/env python3

from time import sleep, time
from os.path import isdir
from os import mkdir
from src.HL_connection import hl_connected
from src.HL_connection import hl_socket
from src.HL_connection import stop_com_hl
from src.ThreadData import ThreadData
from src.affichage import *
from src.affichage import afficher_en_polaire
from src.mesures import mesures

if not isdir("./Logs/"):
    mkdir("./Logs/")

logging.config.fileConfig('./configs/config_log.ini')
_loggerPpl = logging.getLogger("ppl")
_loggerHl = logging.getLogger("hl")

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
    sleep(2)

    # Initialisation de l'affichage
    if not hl_connected:
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
        sleep(0.01)

        # Attendre qu'au moins 1 scan soit effectué
        if not thread_data.is_ready():
            continue
        # Calcul du temps d'exécution : aussi utilisé pour le Kalman
        te = (time() - t)
        t = time()
        # On récupère les données du scan du LiDAR et on fait les traitements
        dico, limits, list_obstacles, list_obstacles_precedente = mesures(te, list_obstacles_precedente, thread_data)

        # Envoi de la position du centre de l'obstacle détécté pour traitement par le pathfinding
        if hl_connected:
            liste_envoyee = []
            for o in list_obstacles:
                angle = o.center
                r = dico[angle]
                liste_envoyee.append(str((r, angle)))
                envoi = ";".join(liste_envoyee)
                envoi = envoi + "\n"
            _loggerHl.debug("envoi au hl: %s.", envoi)
            socket.send(envoi.encode('ascii'))

        # Affichage des obstacles, de la position Kalman, et des points détectés dans chaque obstacle
        else:
            if afficher_en_polaire:
                pass# affichage_polaire(limits, ax, list_obstacles, dico, fig)
            else:
                pass# affichage_cartesien(limits, ax, list_obstacles, dico, fig)

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
