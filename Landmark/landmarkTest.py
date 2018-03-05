from SLAMATH import *
from os.path import exists
from os import mkdir, getcwd
import matplotlib.pyplot as plt
from numpy.random import randint, rand
from time import time, sleep
import csv
import rplidar
import configparser


# plt.xkcd()

def getCesures(mesures, mu_infini):
    """
    Detection des contours dans le scan
    """
    print(len(mesures))
    SEPARATION_CESURE = 100
    SEPARATION_CONTINUITE=20
    cesures = []  # chaque discontinuité trouvée
    itemCount = 0
    newItem = False
    items = []

    for i in range(len(mesures)):
        ri = mesures[i].r
        rim = mesures[i - 1].r
        rimm = mesures[i - 2].r
        if (i < len(mesures) - 2):
            rip = mesures[i + 1].r
            ripp = mesures[i + 2].r
        elif (i == len(mesures) - 2):
            rip = mesures[i + 1].r
            ripp = mesures[0].r
        elif (i == len(mesures) - 1):
            rip = mesures[0].r
            ripp = mesures[1].r

        if (abs(ri - rim) < SEPARATION_CONTINUITE and abs(rim - rimm) < SEPARATION_CONTINUITE and abs(ri - rip) > SEPARATION_CESURE) or (
                abs(ri - rip) < SEPARATION_CONTINUITE and abs(rip - ripp) < SEPARATION_CONTINUITE and abs(ri - rim) > SEPARATION_CESURE) or (
                abs(ri - rip) + abs(ri - rim) > 2 * SEPARATION_CESURE):  # and abs(rim-rimm)+abs(rip-ripp)<50:
            cesures.append(Vec(mesures[i].x, mesures[i].y,mesures[i].id))

            # TODO:récupérer le centre des obstacles, leur largeur
    for i in range(len(cesures)):
        ci = cesures[i]
        cim = cesures[i - 1]
        if (i < len(cesures) - 1):
            cip = cesures[i + 1]
        elif (i == len(cesures) - 1):
            cip = cesures[0]
        if ci.dist(cim) < 200 and ci.dist(cip) > 500:
            theta = (ci.theta + cim.theta) / 2
            r = (ci.r + cim.r) / 2
            plt.plot(r * cos(theta), r * sin(theta), 'go', linewidth=20)
        elif ci.dist(cip) < 200 and ci.dist(cim) > 500:
            theta = (ci.theta + cip.theta) / 2
            r = (ci.r + cip.r) / 2
            plt.plot(r * cos(theta), r * sin(theta), 'go', linewidth=20)
        elif ci.dist(cim) > 500 and ci.dist(cip) > 500:
            theta = ci.theta
            r = ci.r
            plt.plot(ci.x, ci.y, 'go', linewidth=20)
    plt.plot([c.x for c in cesures], [c.y for c in cesures], 'ro', markersize=mu_infini / 3000)
    plt.plot([v.x for v in mesures], [v.y for v in mesures], 's', markersize=1)


def doMeasures():
    PORT_NAME = "/dev/ttyUSB0"
    lidar = rplidar.RPLidar(PORT_NAME)
    info = lidar.get_info()  # info general sur le lidar
    print(info)
    health = lidar.get_health()
    print(health)

    """ PRISE DES MESURES
        Nombre de vitesses : 10
        Nombre de scans par vitesse : 100
    """
    for j in range(0, 11):
        lidar.motor_speed = 200 + 82 * j
        lidar.start()
        lidar.start_motor()
        sleep(5)
        lidar.clean_input()
        for i in range(20):
            with open("./data/data_" + str(j) + "_" + str(i) + ".csv", "w") as datafile:
                print(i, 200 + 82 * j)
                nouveauTour = False
                nb = 0

                for n, scan in enumerate(lidar.iter_measures()):
                    if nouveauTour:
                        datafile.write(str(scan[1]) + ";" + str(scan[2]) + ";" + str(scan[3]) + "\n")
                    if scan[0] and not nouveauTour:
                        nouveauTour = True
                    elif scan[0] and nouveauTour:
                        break
    lidar.stop()
    lidar.stop_motor()
    print("Mesures termine")


def readMesures(path):
    data = []
    with open(path, 'r') as datafile:
        datareader = csv.reader(datafile, delimiter=';')
        id=0
        for i, line in enumerate(datareader):
            if (round(float(line[2])) > 0):
                data.append(Vec(float(line[2]) * cos(2 * pi * float(line[1]) / 360),
                                float(line[2]) * sin(2 * pi * float(line[1]) / 360),id))
                id+=1
    return data


"""
Script principal, trace les graphes de 50 scans en plaçant les bordures(césures) détectées, et en y traçant une ligne depuis l'origine pour plus de visibilité
"""
if __name__ == '__main__':

    config=configparser.ConfigParser()
    if not exists('./graph'):
        mkdir('./graph')
    if not exists('../anglesTest/graph'):
        mkdir('../anglesTest/graph')
    mu_infini = 8000
    sigma = 8

    times = [0 for _ in range(25)]
    for _ in range(1):
        # print("Mesure",i)
        fig = plt.figure(num=None, figsize=(16, 12), dpi=600)
        # Les obstacles aléatoires
        nb_obst = 1
        # doMeasures()
        for i in range(0, 11):
            for j in range(20):
                axes = plt.axes()

                axes.set_xlim(-4000, 4000)
                axes.set_ylim(-4000, 4000)
                axes.axvline(0, 0)
                axes.axhline(0, 0)
                print(i, j)
                sizes = randint(10, 20, nb_obst)
                distances = [randint(50, mu_infini) / mu_infini for _ in sizes]
                angles = [360 * rand() for _ in distances]
                end_angles = [n * 0.9 + angle for n, angle in zip(sizes, angles)]

                # Le générateur de points
                print("currdir:" + getcwd())
                gen = fakeLidar(mu_infini, sigma, angles, end_angles, distances)
                mesures = readMesures("./data/data_" + str(i) + "_" + str(j) + ".csv")
                now = time()

                cesures = getCesures(mesures, mu_infini)
                times[i] += (time() - now)

                plt.savefig("./graph/graph_" + str(i * 82 + 200) + "_" + str(j) + ".svg")
                fig.clear()
            nb_obst += 1
    u = [t / (10 * nb) for t, nb in zip(times, range(1, 26))]
    v = [i for i, _ in enumerate(times)]

# plt.plot(v,u)
# plt.show()
