#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.obstacles import Obstacle
from math import cos, sin, pi, sqrt
from src.kalman import ekf
import numpy as np


def liaison_objets(dico, list_bounds, seuil_association_cartesien, Te, list_obstacles_precedente):
    """
    Fonction qui créé des objets de type Obstacle et retourne une liste de ces obstacles

    :param dico: Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    :param list_bounds: Liste de listes de format [angle début obstacle,angle fin obstacle]
    :param seuil_association_cartesien: Tolerance pour savoir si un nouvel objet est un ancien objet qui s'est déplacé
    :param Te: écart entre 2 scans (en ms ?)
    :param list_obstacles_precedente: Liste d'objets de type Obstacle
    :return: list_obstacles: Liste d'objets de type Obstacle
    """

    list_obstacles = []
    n = len(list_bounds)

    for new_obstacle in range(n):

        distance_min = 12000
        distance_max = 0
        dist_min_ancien_new_obst = distance_min
        ancien_obst_associe = None

        # Calcul milieu obstacles et largeur
        if len(list_bounds) >= 1:
            angle_debut = list_bounds[new_obstacle][0]
            angle_fin = list_bounds[new_obstacle][1]

            if angle_fin < angle_debut:
                center = (abs(angle_debut + angle_fin + 2 * pi) / 2) % (2 * pi)
            else:
                center = abs(angle_debut + angle_fin) / 2
            center = round(center, 4)
            # print("center: ", center)

            if center not in dico.keys():
                for angle in dico.keys():
                    if angle_fin < angle_debut:
                        angle_fin += 2 * pi

                    if angle_debut <= angle <= angle_fin:
                        if angle < 2 * pi:
                            distance = dico[angle]
                        elif angle >= 2 * pi:
                            distance = dico[angle - 2 * pi]

                        if distance > distance_max:
                            distance_max = distance
                        if distance < distance_min:
                            distance_min = distance

                dico[center] = (distance_max + distance_min) / 2

            # print("distance_max: ", distance_max)
            # print("distance_min: ", distance_min)
            # print("dico_center: ", dico[center])
            if angle_fin >= 2 * pi:
                angle_fin = round(angle_fin - 2 * pi, 4)

            # width = max(abs(xmax - xmin), abs(ymax - ymin)) # en degre
            width = sqrt(dico[angle_debut] ** 2 + dico[angle_fin] ** 2 - 2 * dico[angle_debut] * dico[angle_fin] \
                         * cos(abs(angle_fin - angle_debut)))  # Al Kashi
            # print("width: ", width)

            # # print("width: ", width)
        # Creation des objets de type Obstacle
        list_obstacles.append(Obstacle(width, center, dico[center]))
        obstacle_traite = list_obstacles[new_obstacle]

        # Association des anciens obstacles avec les nouveaux obstacles
        if list_obstacles_precedente:
            for precedent_obstacle in list_obstacles_precedente:
                a1 = center
                r1 = dico[a1]
                if obstacle_traite.get_predicted_kalman():
                    a2 = precedent_obstacle.get_predicted_kalman()[1]
                    r2 = precedent_obstacle.get_predicted_kalman()[0]
                else:
                    a2 = precedent_obstacle.get_center()
                    r2 = precedent_obstacle.get_distance()
                distance_entre_objets = sqrt(r1 ** 2 + r2 ** 2 - 2 * r1 * r2 * cos(a2 - a1))

                if distance_entre_objets < dist_min_ancien_new_obst:  # Distance entre le dernier kalman estimé
                    # et la position mesurée du nvel objet
                    dist_min_ancien_new_obst = distance_entre_objets
                    ancien_obst_associe = precedent_obstacle

            if dist_min_ancien_new_obst < seuil_association_cartesien:
                ancien_obst_associe.set_updated(True)
                obstacle_traite.set_ancien_obst_associe(ancien_obst_associe)
                if ancien_obst_associe.get_predicted_kalman() is not None:  # On récupère la valeur de l'ancien objet
                    # car les 2 objets sont en fait les mêmes
                    obstacle_traite.set_predicted_kalman(ancien_obst_associe.get_predicted_kalman()[0],
                                                         ancien_obst_associe.get_predicted_kalman()[1])

            # Kalman
            # y_k: derniere mesure faite avec le lidar -> [obstacle_traite.get_center, dico[center]]
            # x_kalm_prec: ancienne sortie du Kalman
            # p_kalm_prec: ancienne sortie du Kalman
            if obstacle_traite.get_predicted_kalman() is not None:
                x_kalm_prec, p_kalm_prec = ekf(Te, np.array([center, dico[center]]),
                                               obstacle_traite.get_predicted_kalman()[0],
                                               obstacle_traite.get_predicted_kalman()[1])
                obstacle_traite.set_predicted_kalman(x_kalm_prec, p_kalm_prec)
            else:
                r = dico[center]
                x_kalm_prec = np.array([r * cos(center), 0, r * sin(center), 0]).T
                p_kalm_prec = np.identity(4)
                obstacle_traite.set_predicted_kalman(x_kalm_prec, p_kalm_prec)  # Initialisation du
                # Kalman à la 1ère position mesurée de l'obstacle

    list_obstacles_precedente = list_obstacles
    return list_obstacles, list_obstacles_precedente
