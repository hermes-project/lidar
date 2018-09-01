#!/usr/bin/env python3
# coding: utf-8

"""
Les obstacles sont pistés par l'angle par rapport au LIDAR, sa distance et

"""

from collections import deque
import numpy


class Obstacle:
    """"
    Classe permettant de créer des obstacles
    """

    def __init__(self, width, center, distance):
        self.is_moving = False
        self.speed = 0.  # necessite que ce soit des vecteurs # TODO
        self.predicted_position = numpy.array([0, 0])  # [distance, angle] avec la distance en mm  et l'angle en radian
        self.previous_predicted_kalman = None
        self.current_predicted_kalman = None
        self.obstacle_track = deque()  # Les positions precedentes de l'objet en mouvement
        self.updated = False
        self.previous_associated_obstacle = None
        self.width = width  # distance en mm
        self.center = center  # valeur de milieu de l'objet, exprimé grâce à un angle en radian
        self.distance = distance  # distance du milieu de l'objet

    def get_is_moving(self):
        return self.is_moving

    def get_speed(self):
        return self.speed

    def get_predicted_position(self):
        return self.predicted_position

    def get_predicted_kalman(self):
        return self.current_predicted_kalman

    def get_previous_predicted_kalman(self):
        return self.previous_predicted_kalman

    def get_obstacle_track(self):
        return self.obstacle_track

    def get_width(self):
        return self.width

    def get_center(self):
        return self.center

    def get_distance(self):
        return self.distance

    def get_updated(self):
        return self.updated

    def get_previous_associated_obstacle(self):
        return self.previous_associated_obstacle

    def set_is_moving(self, is_moving):
        """

        :param is_moving: bool
        :return:
        """
        self.is_moving = is_moving

    def set_speed(self, speed):
        """

        :param speed: Vec
        :return:
        """
        self.speed = speed

    def set_predicted_position(self, predicted_position):
        """
        Position suivante de l'objet, predite si cet objet est suppose fixe

        :param predicted_position: tuple ([distance, angle] avec l'angle en RADIAN et la distance en mm)
        :return:
        """
        self.predicted_position = predicted_position

    def set_predicted_kalman(self, predicted_kalman_x, predicted_kalman_p):
        """
        Position suivante de l'objet, predite avec Kalman

        :param predicted_kalman_x: vecteur de position et vitesse
        :param predicted_kalman_p: matrice de covariance de l'erreur
        :return:
        """
        self.current_predicted_kalman = [predicted_kalman_x, predicted_kalman_p]

    def set_previous_predicted_kalman(self, previous_predicted_kalman):
        """
        Position suivante de l'objet, predite avec Kalman

        :param previous_predicted_kalman: tuple ([distance, angle] avec l'angle en RADIAN et la distance en mm)
        :return:
        """
        self.previous_predicted_kalman = previous_predicted_kalman

    def append_new_associated_obstacle(self, new_associated_obstacle):
        """
        Ajoute la derniere position de l'objet a sa liste de positions precedentes

        :param new_associated_obstacle: tuple ([distance, angle] avec l'angle en RADIAN et la distance en mm)
        :return:
        """
        self.obstacle_track.append(new_associated_obstacle)

    def remove_track_obstacle(self):
        """
        Enlève la valeur à gauche dans la liste de positions precedentes (piste)

        :return:
        """
        self.obstacle_track.popleft()

    def set_obstacle_track(self, position_piste):
        """
        Met à jour la liste de positions precedentes

        :param position_piste: liste de positions
        :return:
        """
        self.obstacle_track = position_piste

    def set_width(self, width):
        """

        :param width: tuple
        :return:
        """
        self.width = width

    def set_center(self, center):
        """

        :param center: tuple (angle en RADIAN)
        :return:
        """
        self.center = center

    def set_distance(self, distance):
        """

        :param distance: tuple (distance en mm)
        :return:
        """
        self.distance = distance

    def set_updated(self, updated):
        """

        :param updated: bool
        :return:
        """
        self.updated = updated

    def set_previous_associated_obstacle(self, previous_associated_obstacle):
        """
        :param previous_associated_obstacle: objet de type Obstacle
        :return:
        """
        self.previous_associated_obstacle = previous_associated_obstacle
