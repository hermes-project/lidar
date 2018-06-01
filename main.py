#!/usr/bin/env python3
import logging.config
from os import mkdir
from os.path import isdir
from time import sleep, time

from src.HL_connection import hl_connected
from src.HL_connection import hl_socket
from src.HL_connection import stop_com_hl
from src.affichage import init_affichage_polaire, init_affichage_cartesien, affichage_polaire, affichage_cartesien, \
    affichage, afficher_en_polaire
from src.mesures import mesures
from libs import rplidar
from serial.tools.list_ports import comports


if not isdir("./Logs/"):
    mkdir("./Logs/")

logging.config.fileConfig('./configs/config_log.ini')
_loggerPpl = logging.getLogger("ppl")
_loggerHl = logging.getLogger("hl")

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

    try:
        lidar = rplidar.RPLidar(comports()[0].device)  # Tente de se connecter au premier port Serie disponible
    except IndexError:
        _loggerPpl.error("Pas de connexion serie disponible.")
        exit()
    # Attente de quelques tours pour que le lidar prenne sa pleine vitesse et envoie assez de points
    sleep(1)

    # Initialisation de l'affichage
    if affichage:
        if afficher_en_polaire:
            ax, fig = init_affichage_polaire()
        else:
            ax, fig = init_affichage_cartesien()

    # Initialisation des valeurs pour le calcul du temps d'exécution
    t = time()
    te = t

    # Boucle de récupération,de traitement des données, d'envoi et d'affichage
    while True:
        # Tentative bloquante de recuperation de donnees de lidar

        # Calcul du temps d'echantillonnage utilisé pour le Kalman
        te = (time() - t)
        t = time()
        # On récupère les données du scan du LiDAR et on fait les traitements
        dico, limits, list_obstacles, list_obstacles_precedente = mesures(te, list_obstacles_precedente, lidar)

        # Envoi de la position du centre de l'obstacle détécté pour traitement par le pathfinding
        liste_envoyee = []
        envoi = None
        for o in list_obstacles:
            angle = o.center
            r = dico[angle]
            liste_envoyee.append(str((r, angle)))
            envoi = ";".join(liste_envoyee)
            envoi = envoi + "\n"
        _loggerHl.debug("envoi au hl: %s.", envoi)
        if hl_connected and envoi:
            socket.send(envoi.encode('ascii'))
        # Affichage des obstacles, de la position Kalman, et des points détectés dans chaque obstacle
        if affichage:
            if afficher_en_polaire:
                affichage_polaire(limits, ax, list_obstacles, dico, fig)
            else:
                affichage_cartesien(limits, ax, list_obstacles, dico, fig)

except Exception:
    # Arrêt du système
    if hl_connected and socket:
        stop_com_hl(socket)
    _loggerPpl.info("ARRET DEMANDE.")
    if thread_data:
        thread_data.stop_lidar()
        thread_data.join()
        thread_data = None
    _loggerPpl.exception("Erreur lors de l'execution du programme, arret total")

finally:
    # Arrêt du système
    if hl_connected and socket:
        stop_com_hl(socket)
    if thread_data:
        thread_data.stop_lidar()
        thread_data.join()
        thread_data = None
