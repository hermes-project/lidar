#!/usr/bin/env python3
from time import time
from math import pi


def data_cleaner(lidarData, nombre_tours, resolution_degre, distance_infini):
    """
    Fichier avec la fonction qui génère les données. Le Lidar doit être instencié dans le main

    :param distance_infini:
    :param resolution_degre:
    :param lidarData:
    :param nombre_tours: le nombre de tours qu'effectue le LiDAR
    :return: data Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    """

    data = {}
    toRadian = pi / 180.

    for indice in range(len(lidarData)):
        angle_degre = resolution_degre * (indice % int(360. / resolution_degre))
        angle_radian = angle_degre * toRadian
        if angle_radian in data:
            data[angle_radian].append(lidarData[indice])
        else:
            data[angle_radian] = [lidarData[indice]]

    for angle, distances in data.items():
        j = 0
        m = average(distances)
        et = standard_deviation(distances, m)
        while j < len(distances):
            if distances[j] < m - (3 * et) or distances[j] > m + (3 * et):
                distances.pop(j)
            else:
                j += 1
        value = average(distances)
        data[angle] = value
    last_angle=resolution_degre * ((len(lidarData)-1) % int(360. / resolution_degre))*toRadian
    for angle, distance in data.items():
        if distance <10:
            data[angle]=data[last_angle]
        last_angle=angle
    return data


def average(data):
    S = 0.
    n = 0
    for value in data:
        if value > 0:
            S += value
            n += 1
    if n >0:
        return S/n
    else:
        return 0


def standard_deviation(array, m):
    if len(array) == 0:
        return 0
    else:
        return (average([(x - m) ** 2 for x in array])) ** 0.5
