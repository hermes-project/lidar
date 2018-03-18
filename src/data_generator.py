#!/usr/bin/env python3
from time import time
from math import pi


def generator(lidar, nombre_tours, resolution_degre):
    """
    Fichier avec la fonction qui génère les données. Le Lidar doit être instencié dans le main

    :param lidar: Le lidar utilisé
    :param nombre_tours: le nombre de tours qu'effectue le LiDAR
    :param resolution: La résolution utilisée en DEGRES
    :return: data Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    """

    alpha_degre = 0.
    data = {}
    i = 0
    arround = resolution_degre * 10.
    while alpha_degre < 360.:  # Génération des clés dans le dictionnaire
        alpha_radian = round(alpha_degre * 2 * pi / 360, 4)
        data[alpha_radian] = []
        alpha_degre = round((alpha_degre+resolution_degre), 1)

    for measure in lidar.iter_measures():
        if measure[0]:  # Si à TRUE (ie nouveau tour) on incremente
            i += 1

        # Ignorer les valeurs absurdement proches
        if measure[3] == 0:
                continue

        theta_degre = ((round(measure[2]/arround, 1)*arround) % 360)
        # Arrondi a la resolution près. EX : à 0.5 près pour 2,57 et 2,8. round(2,57 / 5 , 1) = 0.5 et 0.5 * 5 = 2.5 .
        # round ( 2,8 / 5 , 1) = 0.6 et 0.6 * 5 = 3
        theta_radian = round(theta_degre * 2 * pi / 360, 4)
        if theta_degre == 360.:
            data[0].append(measure[3])
        else:
            data[theta_radian].append(measure[3])
        if i >= nombre_tours:  # Si nombre_tours tours realise
            break

    for angle, distances in data.items():
        j = 0
        m = average(distances)
        et = standard_deviation(distances, m)
        while j < len(distances):
            if distances[j] < m-(3*et) or distances[j] > m + (3*et):
                distances.pop(j)
            else:
                j += 1
        value = average(distances)
        if value < 10:
            value = 12000
        data[angle] = round(average(distances))

    return data


def average(array):  # TODO : on ne donne pas à une variable le nom d'un type
    if len(array) == 0:
        return 0
    else:
        return sum(array, 0.0) / len(array)


def standard_deviation(array, m):
    if len(array) == 0:
        return 0
    else:
        return (average([(x - m)**2 for x in array]))**0.5
