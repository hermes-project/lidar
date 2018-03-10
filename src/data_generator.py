from rplidar import RPLidar


"""
fichier avec la fonction qui génère les données. Le Lidar doit être instencié dans le main
Entrée : RPLidar, résolution en angle
Sortie : Dictionnaire avec les angles discrétisés en key et les tuples de distance en valeurs
"""



def generator(lidar, resolution):

    alpha = 0.
    data = {}
    i = 0
    arround = resolution * 10.
    while alpha <= 360.: #génération des clés dans le dictionnaire
        data[alpha] = []
        alpha += resolution

    for measure in lidar.iter_measures():
        if measure[0]:
            i += 1
        theta = round(measure[2]/arround,1)*arround # arrondie a la resolution près. EX : à 0.5 près pour 2,57 et 2,8. round(2,57 / 5 , 1) = 0.5 et 0.5 * 5 = 2.5 . round ( 2,8 / 5 , 1) = 0.6 et 0.6 * 5 = 3
        data[theta].append(measure[3])
        if i >= 10 :
            break
    return data
