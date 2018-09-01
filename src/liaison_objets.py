#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""

from src.obstacles import Obstacle
from math import cos, sin, pi, sqrt
from src.kalman import ekf
import numpy as np


def compute_obstacle_features(measures: dict, distance_max: float, distance_min: float,
                              beginning_angle: float, end_angle: float):
    """

    :param measures:
    :param distance_max:
    :param distance_min:
    :param beginning_angle:
    :param end_angle:
    :return:
    """
    if end_angle < beginning_angle:
        center = (abs(beginning_angle + end_angle + 2 * pi) / 2) % (2 * pi)
    else:
        center = abs(beginning_angle + end_angle) / 2
    center = round(center, 4)

    if center not in measures:
        for angle in measures:
            if end_angle < beginning_angle:
                end_angle += 2 * pi
            if beginning_angle <= angle <= end_angle:
                if angle < 2 * pi:
                    distance = measures[angle]
                elif angle >= 2 * pi:
                    distance = measures[angle - 2 * pi]
                if distance > distance_max:
                    distance_max = distance
                if distance < distance_min:
                    distance_min = distance

        measures[center] = (distance_max + distance_min) / 2

    if end_angle >= 2 * pi:
        end_angle = round(end_angle - 2 * pi, 4)

    # width = max(abs(xmax - xmin), abs(ymax - ymin)) # en degre
    width = sqrt(
        measures[beginning_angle] ** 2 + measures[end_angle] ** 2 - 2 * measures[beginning_angle] * measures[
            end_angle]
        * cos(abs(end_angle - beginning_angle)))  # Al Kashi
    return Obstacle(width, center, measures[center])


def filter_position(measures: dict, period: float, processed_obstacle: Obstacle, center):
    """
    Filtre de Kalman
    y_k: derniere mesure faite avec le lidar -> [obstacle_traite.get_center, measures[center]]
    x_kalm_prec: ancienne sortie du Kalman
    p_kalm_prec: ancienne sortie du Kalman

    :param measures:
    :param period:
    :param processed_obstacle:
    :param center:
    :return:
    """

    if processed_obstacle.get_predicted_kalman() is not None:
        x_kalm_prec, p_kalm_prec = ekf(period, np.array([center, measures[center]]),
                                       processed_obstacle.get_predicted_kalman()[0],
                                       processed_obstacle.get_predicted_kalman()[1])
        processed_obstacle.set_predicted_kalman(x_kalm_prec, p_kalm_prec)
    else:
        r = measures[center]
        x_kalm_prec = np.array([r * cos(center), 0, r * sin(center), 0]).T
        p_kalm_prec = np.zeros(4)
        processed_obstacle.set_predicted_kalman(x_kalm_prec, p_kalm_prec)  # Initialisation du
        # Kalman à la 1ère position mesurée de l'obstacle
    return processed_obstacle


def associate_obstacles(measures: dict, bounds: list, distance_threshold: float, period: float,
                        previous_obstacles: list):
    """
    Fonction qui créé des objets de type Obstacle et retourne une liste de ces obstacles

    :param measures: Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    :param bounds: Liste de listes de format [angle début obstacle,angle fin obstacle]
    :param distance_threshold: Tolerance pour savoir si un nouvel objet est un ancien objet qui s'est déplacé
    :param period: écart entre 2 scans (en ms ?)
    :param previous_obstacles: Liste d'objets de type Obstacle
    :return: obstacles, previous_obstacles: Listes d'objets de type Obstacle
    """

    center = None
    obstacles = []

    for new_obstacle in range(len(bounds)):

        distance_min = 12000
        distance_max = 0
        dist_min_ancien_new_obst = distance_min
        previous_associated_obstacle = None
        new_computed_obstacle = None

        # Calcul milieu obstacles et largeur
        if len(bounds) >= 1:
            beginning_angle = bounds[new_obstacle][0]
            end_angle = bounds[new_obstacle][1]
            new_computed_obstacle = compute_obstacle_features(measures, distance_max, distance_min,
                                                              beginning_angle, end_angle)
            center = new_computed_obstacle.get_center()

        # Creation des objets de type Obstacle
        obstacles.append(new_computed_obstacle)
        processed_obstacle = obstacles[new_obstacle]

        # Association des anciens obstacles avec les nouveaux obstacles
        if previous_obstacles:
            for previous_obstacle in previous_obstacles:
                a1 = center
                r1 = measures[a1]
                if processed_obstacle.get_predicted_kalman():
                    a2 = previous_obstacle.get_predicted_kalman()[1]
                    r2 = previous_obstacle.get_predicted_kalman()[0]
                else:
                    a2 = previous_obstacle.get_center()
                    r2 = previous_obstacle.get_distance()
                distance_between_obstacles = sqrt(r1 ** 2 + r2 ** 2 - 2 * r1 * r2 * cos(a2 - a1))

                if distance_between_obstacles < dist_min_ancien_new_obst:  # Distance entre le dernier kalman estimé
                    # et la position mesurée du nvel objet
                    dist_min_ancien_new_obst = distance_between_obstacles
                    previous_associated_obstacle = previous_obstacle

            if dist_min_ancien_new_obst < distance_threshold:
                previous_associated_obstacle.set_updated(True)
                processed_obstacle.set_previous_associated_obstacle(previous_associated_obstacle)
                if previous_associated_obstacle.get_predicted_kalman() is not None:
                    # On récupère la valeur de l'ancien objet
                    # car les 2 objets sont en fait les mêmes
                    processed_obstacle.set_predicted_kalman(previous_associated_obstacle.get_predicted_kalman()[0],
                                                            previous_associated_obstacle.get_predicted_kalman()[1])
                    piste = previous_associated_obstacle.get_piste_obstacle()
                    processed_obstacle.set_obstacle_track(piste)
                    if piste:
                        if len(piste) > 30:
                            processed_obstacle.remove_track_obstacle()
                    processed_obstacle.append_new_associated_obstacle([
                        previous_associated_obstacle.get_predicted_kalman()[0][0],
                        previous_associated_obstacle.get_predicted_kalman()[0][2]])

            obstacles[new_obstacle] = filter_position(measures, period, processed_obstacle, center)

    previous_obstacles = obstacles

    return obstacles, previous_obstacles
