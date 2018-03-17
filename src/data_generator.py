#!/usr/bin/env python3
from time import time


def generator(lidar, nombre_tours, resolution):
    """
    fichier avec la fonction qui génère les données. Le Lidar doit être instencié dans le main

    :param lidar: Le lidar utilisé
    :param nombre_tours: le nombre de tours qu'effectue le LiDAR
    :param resolution: La résolution utilisée
    :return: data Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
    """

    alpha = 0.
    data = {}
    i = 0
    arround = resolution * 10.
    while alpha < 360.: # génération des clés dans le dictionnaire
        data[alpha] = []
        alpha = round((alpha+resolution), 1)

    for measure in lidar.iter_measures():
        if measure[0]:  # si à TRUE (ie nouveau tour) on incremente
            i += 1

        # Ignorer les valeurs absurdement proches
        if measure[3] == 0:
                continue

        theta = (round(measure[2]/arround, 1)*arround) % 360
        # arrondie a la resolution près. EX : à 0.5 près pour 2,57 et 2,8. round(2,57 / 5 , 1) = 0.5 et 0.5 * 5 = 2.5 .
        # round ( 2,8 / 5 , 1) = 0.6 et 0.6 * 5 = 3
        if theta == 360.:
            data[0].append(measure[3])
        else:
            data[theta].append(measure[3])
        if i >= nombre_tours : # si nombre_tours tours realise
            break
    for angle, distances in data.items():
        j = 0
        m = average(distances)
        et = standard_deviation(distances, m)
        while j < len(distances) :
            if distances[j] < m-(3*et) or distances[j] > m + (3*et):
                distances.pop(j)
            else:
                j += 1
        value=average(distances)
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
