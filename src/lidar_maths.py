from math import pow, sqrt, sin, cos, atan2, pi
from numpy.random import normal


class Vec:
    def __init__(self, x, y, _id):
        self.x = x
        self.y = y
        self.r = sqrt(pow(self.x, 2)+pow(self.y, 2))
        self.theta = atan2(self.y, self.x)
        self.id = _id

    def dist(self, other_vec):
        return sqrt((other_vec.x-self.x)**2+(other_vec.y-self.y)**2)

    def angle_to(self, other_vec):
        return other_vec.theta-self.theta

    def dot(self, other_vec):
        return other_vec.x*self.x+other_vec.y*self.y


class Line:
    def __init__(self, vec1, vec2):
        self.vec1 = vec1
        self.vec2 = vec2
        self.length = vec1.dist(vec2)
        self.theta = atan2(vec2.y-vec1.y, vec2.x-vec1.x)


def fakeLidar(mu=1000, sigma=3, angles_min=None, angles_max=None, distances=None):
    """
    Retourne un générateur de mesures fournissant 400 mesures distances gaussiennes avec une moyenne de mu
    et d'écart-type sigma, avec n portions à mu/3 entre les angles anglemin et anglemax
    """
    if angles_max is None:
        angles_max = [0.0]
    if angles_min is None:
        angles_min = [0.0]
    if distances is None:
        distances = [1000 for _ in range(len(angles_max))]
    angle = 0
    increment = 0.9
    nb_objs = []
    for m, M in zip(angles_min, angles_max):
        nb_objs.append(round((M-m)/increment))
    nbfond = 400-sum(nb_objs)

    for i in range(400):
        if angle > 360:
            angle = 0
        val=normal(mu, sigma)
        for m, M, r in zip(angles_min, angles_max, distances):
            if m < angle < M:
                val = normal(r*mu, sigma)
        yield 2*pi*angle/360.0, val
        angle += increment
