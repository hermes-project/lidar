#!/usr/bin/env python3


class Obstacle:
    """"Classe permettant de créer des obstacles"""

    isMoving = False
    speed = 0. #necessite que ce soit des vecteurs
    predictedPosition = [0,0]
    updated = False

    def __init__(self, width, center):
        self.width = width  # correspond à la liste des données (angle , distances ) de l'obstacle
        self.center = center # valeur de milieu de l'objet calculé selon une méthode défini

    def get_isMoving(self):
        return self.isMoving
    def get_speed(self):
        return self.speed
    def get_predictedPosition(self):
        return self.predictedPosition
    def get_width(self):
        return self.width
    def get_center(self):
        return self.center
    def get_updated(self):
        return self.updated

    def set_isMoving(self, bool):
        self.isMoving = bool
    def set_speed(self, vector):
        self.speed = vector
    def set_predictedPosition(self, tuple):
        self.predictedPosition = tuple
    def set_width(self,dictionnary):
        self.width = dictionnary
    def set_center(self, tuple):
        self.center = tuple
    def set_updated(self,bool):
        self.updated = bool





