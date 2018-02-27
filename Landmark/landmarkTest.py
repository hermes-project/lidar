from SLAMATH import *
from os.path import exists
from os import mkdir
import matplotlib.pyplot as plt
from numpy.random import randint,rand
from time import time
#plt.xkcd()




def getMesures(generateur):
    """
    Récupération des mesures
    """
    mesures=[]
    for i,mesurevide in enumerate(generateur):
        mesures.append(Vec(mesurevide[1]*cos(mesurevide[0]),mesurevide[1]*sin(mesurevide[0])))
        if i > 400:
            break
    return mesures




def getCesures(mesures,mu_infini):
    """
    Detection des contours dans le scan
    """
    SEPARATION_MIN=50
    cesures=[] #chaque discontinuité trouvée
    itemCount=0
    newItem = False
    items=[]

    for i in range(len(mesures)):
        ri=mesures[i].r
        rim=mesures[i-1].r
        rimm=mesures[i-2].r
        if(i<len(mesures)-2):
            rip = mesures[i + 1].r
            ripp = mesures[i + 2].r
        elif(i==len(mesures)-2):
            rip=mesures[i+1].r
            ripp=mesures[0].r
        elif(i==len(mesures)-1):
            rip=mesures[0].r
            ripp=mesures[1].r


        if (abs(ri-rim)<20 and abs(rim-rimm)<20 and abs(ri-rip)>SEPARATION_MIN) or (abs(ri-rip)<20 and abs(rip-ripp)<20 and abs(ri-rim)>SEPARATION_MIN) or (abs(ri-rip)+abs(ri-rim)>2*SEPARATION_MIN):# and abs(rim-rimm)+abs(rip-ripp)<50:
            cesures.append(Vec(mesures[i].x,mesures[i].y))
            if not newItem:
                newItem=True
                itemCount=0
            elif ri<mu_infini*0.98:
                plt.plot([0, mesures[i].x], [0, mesures[i].y], 'b-', linewidth=0.35)
                itemCount += 1
            if(itemCount==2 and ri>mu_infini*0.98):
                newItem=False


            #TODO:récupérer le centre des obstacles, leur largeur
    plt.plot([c.x for c in cesures],[c.y for c in cesures],'ro',markersize=mu_infini/3000)



"""
Script principal, trace les graphes de 50 scans en plaçant les bordures(césures) détectées, et en y traçant une ligne depuis l'origine pour plus de visibilité
"""
if __name__ == '__main__':
    if not exists('./graphs'):
        mkdir('./graphs')
    mu_infini = 8000
    sigma = 8

    axes = plt.axes()
    times=0
    for i in range(50):
        print("Mesure",i)
        axes.set_xlim(-mu_infini*1.05, mu_infini*1.05)
        axes.set_ylim(-mu_infini*1.05, mu_infini*1.05)
        axes.axhline(0, 0,ls="--",linewidth=0.35,color="g")
        axes.axvline(0, 0,ls="--",linewidth=0.35,color="g")
        # Les obstacles aléatoires
        nb_obst = randint(3,6)

        sizes = randint(10, 20, nb_obst)
        distances = [abs(normal(mu_infini/2,mu_infini/5)) / mu_infini for _ in sizes]
        angles = [360 * rand() for _ in distances]
        end_angles = [n * 0.9 + angle for n, angle in zip(sizes, angles)]

        # Le générateur de points

        gen = fakeLidar(mu_infini, sigma, angles, end_angles, distances)

        mesures=getMesures(gen)
        now=time()
        cesures=getCesures(mesures,mu_infini)
        times+=time()-now

        plt.plot([v.x for v in mesures],[v.y for v in mesures],'s',markersize=0.1)
        plt.savefig('./graphs/'+str(i)+'.svg', dpi=300)
        axes.clear()
    print(times/50)