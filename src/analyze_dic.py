from src.lidar_maths import fakeLidar
import configparser
from matplotlib import pyplot as plt
from math import cos,sin,pi
from numpy.random import rand, randint

def analyze_dic(raw_dict):
    list_bounds=[]
    item=False
    precedent = False
    #Récupération des données de config
    config=configparser.ConfigParser()
    config.read('../config.ini')
    precision=config['MESURES']['precision']
    distance_max=config['DETECTION']['distance_max']
    distance_infini=config['DETECTION']['distance_infini']
    print(precision,distance_infini,distance_max)
    last_status=False
    for i,(angle, distance) in enumerate(raw_dict.items()):
        if i>0:
            if not item and not precedent and distance<=3000:
                list_bounds.append([angle])
                item=True
                precedent=True
            elif item and distance>=3000:
                list_bounds[-1].append(float(angle)-float(precision))
                item=False
                precedent=False
        if i==0:
            first=(angle,distance)

    #On traite le premier item en dernier pour avoir accès au dernier
    if not item and not precedent and first[1]<=3000:
        list_bounds.append([item[0]])
    elif item and first[1]>=3000:
        list_bounds[-1].append(first[0]-precision)
    print(list_bounds)
    return list_bounds

angles=[x/10.0 for x in range(0,3600,5)]
distances=randint(200,8000,len(angles))

dico=dict(zip(angles,distances))
print(dico)
analyze_dic(dico)