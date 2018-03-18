#!/usr/bin/env python3


def analyze_dic(raw_dict, distance_max):
    """
    Fonction d'analyse de dictionnaire de valuers

    :param raw_dict: Dictionnaire au format {angle en radian:distance associée en mm}
    :param distance_max: distance sous laquelle on considère un obstacle (mm)
    :return: list_bounds une liste contenant les angles ou couples d'angles (radians) associés aux objet détectés
    """

    list_bounds = []
    item = False
    precedent = False
    last_angle = 0
    to_delete = []

    # On ignore les distances nulles, car absurdes
    for k, v in raw_dict.items():
        if v == 0:
            to_delete.append(k)

    for k in to_delete:
        del raw_dict[k]

    for i, (angle, distance) in enumerate(raw_dict.items()):
        if i > 0 and distance > 10:
            if not item and not precedent and distance <= distance_max:
                list_bounds.append([angle])
                item = True
                precedent = True
            elif item and distance >= distance_max:
                list_bounds[-1].append(last_angle)
                item = False
                precedent = False
            last_angle = angle
        if i == 0:
            first = (angle, distance)

    # On traite le premier item en dernier pour avoir accès au dernier
    if first[1] > 10:
        if not item and not precedent and first[1] <= distance_max:
            list_bounds.append([first[0]])
        elif item and first[1] >= 3000:
            list_bounds[-1].append(first[0])
    n = len(list_bounds)

    for obstacle in range(n):
        if len(list_bounds[obstacle]) == 1:
            list_bounds[obstacle].append(list_bounds[obstacle][0])

    return list_bounds

