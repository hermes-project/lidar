#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.obstacles import Obstacle

def liaison_objets( dico,list_bounds,tolerance_predicted_fixe,tolerance_Kalman ):
    """
    Fonction qui créé des objets de type Obstacle et retourne une liste de ces obstacles

    :param dico:
    :param list_bounds: Liste de listes de format [angle début obstacle,angle fin obstacle]
    :param tolerance:
    :param seuil:
    :return: list_obstacles: liste d'objets de type Obstacle
    """

    list_obstacles = []
    n = len(list_bounds)
    distance_min = 12000
    distance_max = 0

    for obst in range(n):
        # Calcul milieu obstacles et largeur
        if len(list_bounds) >= 1:
            angle_min = list_bounds[obst][0]
            angle_max = list_bounds[obst][1]
            center = abs( angle_min+angle_max ) / 2

            if center not in dico.keys():
                for angle in dico.keys():
                    if angle_min<=angle<=angle_max:
                        distance = dico[angle]
                        if distance>distance_max:
                            distance_max = distance
                        if distance<distance_min:
                            distance_min = distance
                dico[center] = (distance_max+distance_min)/2
            width = max(abs(angle_max - angle_min), (distance_max-distance_min))

        # Creation des objets de type Obstacle
        list_obstacles.append(Obstacle(width, center))  # TODO :  width n'est pas défini
        obstacle_traite = list_obstacles[obst]

        # Calcul predicted_position: la position predite de l'obstacle a l'instant t+1 s'il ne bouge pas

        predictedPosition = center # TODO quand on aura le deplacement du robot
        obstacle_traite.set_predictedPosition( predictedPosition )

        # Update et categorisation des obstacles

        if abs( center-predictedPosition ) < tolerance_predicted_fixe: #on a alors un obstacle fixe
            obstacle_traite.set_updated( True )
            
        else:

            # Calcul de la position predite avec Kalman dans le cas d'un objet mobile
            predicted_Kalman = center #TODO

            if abs( center-predicted_Kalman ) < tolerance_Kalman:
                obstacle_traite.set_isMoving(True)  # on a un objet mobile
                obstacle_traite.set_updated(True)
                obstacle_traite.set_predicted_Kalman(predicted_Kalman)
                obstacle_traite.set_new_position_piste( center ) #les positions precedentes de l'objet en mouvement

            else:
                obstacle_traite.set_updated(False)
                list_obstacles.remove(obst)

    return list_obstacles







