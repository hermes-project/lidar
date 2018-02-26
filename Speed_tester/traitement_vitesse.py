import csv

from rplidar import RPLidar
from time import sleep
import matplotlib.pyplot as plt

PORT_NAME = "COM16"
ANGLE_INF = 265
ANGLE_SUP = 285
INIT_SPEED = 200 #PWM initial
INCREMENT_SPEED = 82 #on incrementera 10 fois pour arriver a 1020 MAX = 1023

SPEED = INIT_SPEED

SPEED = INIT_SPEED
for i in range(11):

    mesure = {} # dictionnaire des angles de mesure

    file = open("./data_"+str(SPEED)+".csv", "r")
    data = csv.reader(file, delimiter=";")

    for row in data :
        angle = round(float(row[1]),0)
        if angle <= ANGLE_SUP and angle >= ANGLE_INF:

            if not angle in mesure :
                mesure[angle] = {}
            distance = float(row[2])
            if distance in mesure[angle]: # si la distance est deja repertorie
                value = mesure.get(angle)
                value[distance] += 1
                mesure[angle] = value
            else:
                value = mesure.get(angle)
                value[distance] = 1
                mesure[angle] = value

    for angles in mesure.keys():
        dico = mesure[angles]
        list = sorted(dico.items())
        x, y = zip(*list)
        print(angles,sum(y))
        somme = 0.
        for i in range(len(x)):
            somme += x[i]*y[i]
        moyenne = somme / sum(y)
        print(moyenne)
        x_2 = [moyenne-1,moyenne,moyenne+1]
        y_2 = [0,25,0]
        plt.plot(x,y)
        plt.plot(x_2,y_2,'r')
        plt.savefig('./mesures/test_vitesse/'+str(SPEED)+'_'+str(angles)+'.png')
        plt.clf()
    SPEED += INCREMENT_SPEED
print(mesure)