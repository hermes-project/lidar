#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.obstacles import Obstacle
from math import cos, sin, pi, sqrt


def liaison_objets(dico, list_bounds, tolerance_predicted_fixe, tolerance_kalman):
    """
    Fonction qui créé des objets de type Obstacle et retourne une liste de ces obstacles

    :param dico: Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    :param list_bounds: Liste de listes de format [angle début obstacle,angle fin obstacle]
    :param tolerance_predicted_fixe: Tolerance pour savoir si l'objet est reste fixe
    :param tolerance_kalman: Tolerance pour savoir si l'objet est alle a sa position predite avec Kalman
    :return: list_obstacles: Liste d'objets de type Obstacle
    """

    list_obstacles = []
    n = len(list_bounds)

    for obst in range(n):

        distance_min = 12000
        distance_max = 0
        predicted_position = [0, 0]
        predicted_kalman = [0, 0]
        
        # Calcul milieu obstacles et largeur
        if len(list_bounds) >= 1:
            angle_debut = list_bounds[obst][0]
            angle_fin = list_bounds[obst][1]
            # xmin = dico[angle_debut] * cos(-angle_debut * 2 * pi / 360)
            # xmax = dico[angle_fin] * cos(-2 * pi * angle_fin / 360)
            # ymin = dico[angle_debut] * sin(-angle_debut * 2 * pi / 360)
            # ymax = dico[angle_fin] * sin(-2 * pi * angle_fin / 360)

            if angle_fin < angle_debut:
                center = (abs(angle_debut + angle_fin + 2*pi) / 2)%(2*pi)
            else:
                center = abs(angle_debut + angle_fin) / 2
            center = round(center, 4)
            print("center: ", center)

            if center not in dico.keys():
                for angle in dico.keys():
                    if angle_fin < angle_debut:
                        angle_fin += 2*pi

                    if angle_debut <= angle <= angle_fin:
                        if angle < 2*pi:
                            distance = dico[angle]
                        elif angle >= 2*pi:
                            distance = dico[angle - 2*pi]

                        if distance > distance_max:
                            distance_max = distance
                        if distance < distance_min:
                            distance_min = distance
                print("distance_max: ", distance_max)
                print("distance_min: ", distance_min)
                dico[center] = (distance_max + distance_min)/2
                print("dico_center: ", dico[center])

            if angle_fin > 2*pi:
                angle_fin = round(angle_fin - 2 * pi, 4)

            # width = max(abs(xmax - xmin), abs(ymax - ymin)) # en degre
            width = sqrt(dico[angle_debut]**2 + dico[angle_fin]**2 - 2 * dico[angle_debut] * dico[angle_fin] \
                    * cos(abs(angle_fin - angle_debut)))  # Al Kashi
            print("width: ", width)

        # Creation des objets de type Obstacle
        list_obstacles.append(Obstacle(width, center))
        obstacle_traite = list_obstacles[obst]

        # Calcul predicted_position: la position predite de l'obstacle a l'instant t+1 s'il ne bouge pas

        predicted_position[0] = dico[center]  # TODO quand on aura le deplacement du robot
        predicted_position[1] = center  # TODO quand on aura le deplacement du robot
        obstacle_traite.set_predicted_position(predicted_position)

        # Update et categorisation des obstacles

        if abs(center-predicted_position[1]) < tolerance_predicted_fixe[1] and abs(dico[center]-predicted_position[0])\
                < tolerance_predicted_fixe[0]:  # On a alors un obstacle fixe
            obstacle_traite.set_updated(True)
            
        else:

            # Calcul de la position predite avec Kalman dans le cas d'un objet mobile
            predicted_kalman[0] = dico[center]  # TODO
            predicted_kalman[1] = center  # TODO

            if abs(center - predicted_kalman[1]) < tolerance_kalman[1] and abs(dico[center] - predicted_kalman[0]) \
                    < tolerance_kalman[0]:  # On a alors un obstacle fixe
                obstacle_traite.set_isMoving(True)  # On a un objet mobile
                obstacle_traite.set_updated(True)
                obstacle_traite.set_predicted_kalman(predicted_kalman)
                obstacle_traite.set_new_position_piste(center)  # Les positions precedentes de l'objet en mouvement

            else:
                obstacle_traite.set_updated(False)
                list_obstacles.remove(obst)

    return list_obstacles







