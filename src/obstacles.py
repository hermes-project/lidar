#!/usr/bin/env python3
# coding: utf-8
from collections import deque
import numpy


class Obstacle:
    """"
    Classe permettant de créer des obstacles
    """

    def __init__(self, width, center, distance):
        self.isMoving = False
        self.speed = 0.  # necessite que ce soit des vecteurs # TODO
        self.predictedPosition = numpy.array([0, 0])  # [distance, angle] avec la distance en mm  et l'angle en radian
        self.ancienPredictedKalman = None
        self.predictedKalman = None
        self.pisteObstacle = deque()  # Les positions precedentes de l'objet en mouvement
        self.updated = False
        self.ancienObstacle = None
        self.width = width  # distance en mm
        self.center = center  # valeur de milieu de l'objet, exprimé grâce à un angle en radian
        self.distance = distance  # distance du milieu de l'objet

    def get_is_moving(self):
        return self.isMoving

    def get_speed(self):
        return self.speed

    def get_predicted_position(self):
        return self.predictedPosition

    def get_predicted_kalman(self):
        return self.predictedKalman

    def get_ancien_predicted_kalman(self):
        return self.ancienPredictedKalman

    def get_piste_obstacle(self):
        return self.pisteObstacle

    def get_width(self):
        return self.width

    def get_center(self):
        return self.center

    def get_distance(self):
        return self.distance

    def get_updated(self):
        return self.updated

    def get_ancien_obst_associe(self):
        return self.ancienObstacle

    def set_is_moving(self, is_moving):
        """

        :param is_moving: bool
        :return:
        """
        self.isMoving = is_moving

    def set_speed(self, vitesse):
        """

        :param vitesse: Vec
        :return:
        """
        self.speed = vitesse

    def set_predicted_position(self, predicted_position):
        """
        Position suivante de l'objet, predite si cet objet est suppose fixe

        :param predicted_position: tuple ([distance, angle] avec l'angle en RADIAN et la distance en mm)
        :return:
        """
        self.predictedPosition = predicted_position

    def set_predicted_kalman(self, predicted_kalman_x, predicted_kalman_p):
        """
        Position suivante de l'objet, predite avec Kalman

        :param predicted_kalman_x: vecteur de position et vitesse
        :param predicted_kalman_p: matrice de covariance de l'erreur
        :return:
        """
        self.predictedKalman = [predicted_kalman_x, predicted_kalman_p]

    def set_ancien_predicted_kalman(self, ancien_predicted_kalman):
        """
        Position suivante de l'objet, predite avec Kalman

        :param ancien_predicted_kalman: tuple ([distance, angle] avec l'angle en RADIAN et la distance en mm)
        :return:
        """
        self.ancienPredictedKalman = ancien_predicted_kalman

    def set_new_position_piste(self, new_position_piste):
        """
        Ajoute la derniere position de l'objet a sa liste de positions precedentes

        :param new_position_piste: tuple ([distance, angle] avec l'angle en RADIAN et la distance en mm)
        :return:
        """
        self.pisteObstacle.append(new_position_piste)

    def remove_point_piste(self):
        """
        Enlève la valeur à gauche dans la liste de positions precedentes (piste)

        :return:
        """
        self.pisteObstacle.popleft()

    def set_position_piste(self, position_piste):
        """
        Met à jour la liste de positions precedentes

        :param position_piste: liste de positions
        :return:
        """
        self.pisteObstacle = position_piste

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

    def set_ancien_obst_associe(self, ancien_obst_associe):
        """
        :param ancien_obst_associe: objet de type Obstacle
        :return:
        """
        self.ancienObstacle = ancien_obst_associe
