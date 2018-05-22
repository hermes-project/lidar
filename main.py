#!/usr/bin/env python3
from time import sleep, time

from src.HL_connection import HL_connected
from src.HL_connection import HL_socket
from src.HL_connection import stop_com_HL
from src.ThreadData import ThreadData
from src.affichage import *
from src.mesures import mesures

list_obstacles_precedente = []  # Liste des positions des anciens obstacles
threadData = ThreadData()


def stop_handler(thread):
    print("ARRET DEMANDE")
    thread.stopLidar()
    thread.join()


try:
    # Creation de socket pour communiquer avec le HL
    socket = HL_socket()
    # Le Thread recevant les donnees
    threadData.start()
    sleep(2)  # Attente de quelques tours pour que le lidar prenne sa pleine vitesse et envoie assez de points
    if not HL_connected:
        ax, fig = init_affichage_cartesien()

    t = time()
    Te = t

    while True:
        if not threadData.isReady():
            continue
        sleep(0.05)
        Te = (time() - t)
        t = time()

        dico, limits, list_obstacles, list_obstacles_precedente = mesures(Te, list_obstacles_precedente, threadData)

        if HL_connected:
            for o in list_obstacles:
                angle = o.center
                r = dico[angle]
                socket.send([r, angle])
        else:
            affichage_cartesien(limits, ax, list_obstacles, dico, fig)

        print("Temps d'execution:", t)

finally:
    stop_com_HL(socket)
    stop_handler(threadData)
