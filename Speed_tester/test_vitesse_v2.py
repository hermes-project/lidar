#!/usr/bin/env python3
""" INITIALISATION """
import csv
from numpy import var
from collections import OrderedDict
from rplidar import RPLidar
from time import sleep, time
import matplotlib.pyplot as plt
plt.xkcd()
PORT_NAME = "/dev/ttyUSB0"
ANGLE_INF = 267
ANGLE_SUP = 273
INIT_SPEED = 200  # PWM initial
INCREMENT_SPEED = 82  # on incrementera 10 fois pour arriver a 1020 MAX = 1023

SPEED = INIT_SPEED

lidar = RPLidar(PORT_NAME)
info = lidar.get_info()  # info general sur le lidar
print(info)
health = lidar.get_health()
print(health)

""" PRISE DES MESURES
    Nombre de vitesses : 10
    Nombre de scans par vitesse : 100
"""
for i in range(11):

    outfile = open('./data_' + str(SPEED) + '.csv', 'w')  # on cree un csv par vitesse
    print('Mesures à SPEED = %d' % SPEED)
    lidar.start_motor()
    lidar._motor_speed = SPEED  # on set la vitesse du lidar

    start_time = time() # on va faire des mesures pendant 10 secondes pour chaque vitesse

    for j, scan in enumerate(lidar.iter_measures()):  # on realise 100 scans a la vitesse qu'on insere dans le csv cree
        timer_10 = time()
        if timer_10 - start_time > 20. :
            break
        if scan[1] >= 12:
            if scan[3] > 0. :
                line = str(scan[1]) + ";" + str(scan[2]) + ";" + str(scan[3])
                outfile.write(line + '\n')
    lidar.stop()  # on arrete le lidar pour que toute les mesures soit realise dans les meme condition que la premiere valeur
    lidar.stop_motor()
    outfile.close()
    SPEED += INCREMENT_SPEED  # on incremente la vitesse pour la prochaine mesure

    sleep(5)  # timer pour que le lidar soit bien a l arret

print("Mesures termine")

# TODO : TRAITEMENT DES DONNEES

""" TRAITEMENT DES DONNEES
    TEST à differentes precisions : 1° ; 0.5° et 0.1°
    INFORMATIONS : Distance utile : 3m : 1° = 52,3 mm  ; 0.5° = 26,2mm et 0.1° = 5,2mm

    Pour chaque fichier (1 fichier = 1 vitesse), on discretise nos mesures selon les differentes precisions. 
    On réalise alors un tableau qui pour chaque valeur d'angle discretisé, donne la fréquence d'apparition d'une distance.
    On trace la courbe fréquence = f(distance) qu'on save.

    LE LIDAR DONNE AUSSI UNE VALEUR DE QUALITE DE MESURE : EN PRATIQUE, ICI, LA QUALITE EST EGALE A 15. ON PEUT RECOMMENCER LE PROCESSUS EN ENLEVANT LES VALEUR DONC LA QUALITE EST INFERIEUR A 15 POUR OBSERVER LES DIFFERENCES

    A suivre
"""

""" TRAITEMENT 1° """
SPEED = INIT_SPEED
ecart_max=0
intervalEcarts=[i for i in range(5,50,5)]
nbEcartsInterval=[0 for i in range(1,50,5)]
nb_ecart=0
nb_mesures=0
variances=[]


for i in range(11):
    mesure = OrderedDict() # dictionnaire des angles de mesure

    file = open("./measures/data_"+str(SPEED)+".csv", "r")
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
        nb_mesures+=1
        dico = mesure[angles]
        list = sorted(dico.items())
        x, y = zip(*list)
        variances.append(var(x))
        ecart=max(x)-min(x)
        if(ecart>ecart_max):ecart_max=ecart
        for p in range(len(intervalEcarts)):
            if(ecart>intervalEcarts[p]):nbEcartsInterval[p]+=1
        print("ecart:{} min:{} max:{}".format(ecart,min(x),max(x)))
        print("Angle:",angles," Nombre de points: ",sum(y))
        somme = 0.
        for i in range(len(x)):
            somme += x[i]*y[i]
        moyenne = somme / sum(y)
        print("Moyenne: ",moyenne)
        x_2 = [moyenne]
        y_2 = [0,25,0]
        #plt.plot(x,y, 'bo')
        #plt.plot(x_2,y_2,'ro')
        #plt.title("v="+str(SPEED)+" angle:"+str(angles))
        #plt.savefig('./graph/'+str(SPEED)+'_'+str(angles)+'.png')
        #plt.clf()
        print("\n")
    SPEED += INCREMENT_SPEED
print(mesure)
print(ecart_max)
print("Ecarts minimaux considérés: ",intervalEcarts," & Nombre de valeurs supérieures à ces écarts: ", nb_mesures,[i/nb_mesures for i in nbEcartsInterval])
mesure=OrderedDict(sorted(mesure.items()))
for i,l in mesure.items():
    print(i,len(l))