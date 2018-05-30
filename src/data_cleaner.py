#!/usr/bin/env python3
# coding: utf-8
from collections import OrderedDict
from math import pi


def data_cleaner(lidar_data, resolution_degre):
    """
    Fichier avec la fonction qui génère les données. Le Lidar doit être instencié dans le main

    :param lidar_data: données brutes du LiDAR
    :param resolution_degre: La résolution utilisée en DEGRES
    :return: data Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    """

    data = OrderedDict()
    to_radian = pi / 180.

    for indice in range(len(lidar_data)):
        angle_degre = resolution_degre * (indice % int(360. / resolution_degre))
        angle_radian = round(angle_degre * to_radian, 4)
        if angle_radian in data:
            data[angle_radian].append(lidar_data[indice])
        else:
            data[angle_radian] = [lidar_data[indice]]

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
    last_angle = round(resolution_degre * ((len(lidar_data) - 1) % int(360. / resolution_degre)) * to_radian, 4)
    for angle, distance in data.items():
        if distance < 10:
            data[angle] = data[last_angle]
        last_angle = angle
    print("FINICLEANER")
    return data


def average(data):
    s = 0.
    n = 0
    for value in data:
        if value > 0:
            s += value
            n += 1
    if n > 0:
        return s/n
    else:
        return 0


def standard_deviation(array, m):
    if len(array) == 0:
        return 0
    else:
        return (average([(x - m) ** 2 for x in array])) ** 0.5
