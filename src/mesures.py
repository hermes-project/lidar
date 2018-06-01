#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import time

from src.analyze_dic import analyze_dic
from src.data_cleaner import data_cleaner
from src.liaison_objets import liaison_objets
import configparser
import logging.config

config = configparser.ConfigParser()
config.read('./configs/config.ini', encoding="utf-8")
nombre_tours = float(config['MESURES']['nombre_tours'])
resolution_degre = float(config['MESURES']['resolution_degre'])
distance_max = int(config['DETECTION']['distance_max'])
distance_infini = int(config['DETECTION']['distance_infini'])
ecart_min_inter_objet = int(config['DETECTION']['ecart_min_inter_objet'])
seuil_association = int(config['OBSTACLES FIXES OU MOBILES']['seuil_association'])

_loggerRoot = logging.getLogger("ppl")
_loggerAffichage = logging.getLogger("affichage")

_loggerPpl = logging.getLogger("ppl")


def data_generator(lidar):
    data_list = [0 for _ in range(int((360. / resolution_degre)))]
    previous_bool = False
    around = resolution_degre * 10
    for newTurn, quality, angle, distance in lidar.iter_measures():  # on recupere les valeurs du lidar
        if newTurn and not previous_bool:  # Si True precede d un False, on est sur un nouveau tour
            # On enregistre le tour scanne dans la queue, sous forme de liste de distances
            print(data_list)
            return data_list

        elif not newTurn:
            previous_bool = False
        angle = ((round(angle / around, 1) * around) % 360.)
        # l'indice dans la liste determine l'angle du lidar, on reduit ainsi la liste.
        data_list[int(angle / resolution_degre)] = distance


def mesures(te, list_obstacles_precedente, lidar):
    """
    Récupération et traitements de données.

    """
    # Mise en forme des donnees, avec un dictionnaire liant angles a la distance associee,
    # et moyennant les distances si il y a plusieurs tours effectues

    lidar_data = data_generator(lidar)
    dico = data_cleaner(lidar_data, resolution_degre)
    _loggerPpl.debug("dico : %s        ", dico)

    # Detection des bords d'obstacles
    limits = analyze_dic(dico, distance_max, ecart_min_inter_objet)
    # _loggerAffichage.info("Ostacles détectés aux angles:", limits)

    # Mise a jour des obstacles detectes, incluant le filtre de kalman
    list_obstacles, list_obstacles_precedente = liaison_objets(dico, limits, seuil_association,
                                                               te, list_obstacles_precedente)

    return dico, limits, list_obstacles, list_obstacles_precedente
