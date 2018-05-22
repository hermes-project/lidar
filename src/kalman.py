#!/usr/bin/env python3
# coding: utf-8
from numpy import array, eye, set_printoptions
from math import cos, sin
from numpy.linalg import inv
import configparser
set_printoptions(suppress=True)

config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")
tolerance_predicted_fixe_r = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe_r'])
tolerance_predicted_fixe_theta = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_predicted_fixe_theta'])
tolerance_predicted_fixe = [tolerance_predicted_fixe_r, tolerance_predicted_fixe_theta]
tolerance_kalman_r = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_kalman_r'])
tolerance_kalman_theta = int(config['OBSTACLES FIXES OU MOBILES']['tolerance_kalman_theta'])
tolerance_kalman = [tolerance_kalman_r, tolerance_kalman_theta]


def isnan(x):
    return x != x


def ekf(te, y_k, x_kalm_prec, p_kalm_prec):
    """
    Extended Kalman Filter:
    Applique le filtre de kalman éendu, fournissant la position estimée x_k|k,
    à partir de la mesure y_k et la position estimée précédente x_k-1|k-1
    Met aussi à jours la matrice de covariances estimée
    :param te: Temps écoulé depuis la dernière mesures
    :param y_k: Le vecteur des mesures, sous la forme numpy.array([angle,distance])
    :param x_kalm_prec: Le vecteur position estimée précédent x_k-1|k-1,
    sous la forme numpy.array([x,vitesse_x,y,vitesse_y])
    :param p_kalm_prec: La matrice de covariance précédente p_k-1|k-1, sous la forme d'un array numpy de taille 4x4,
    initialement c'est la matrice identité (numpy.eye(4)) ou nulle (numpy.zeros(4))
    :return: x_kalm, p_kalm: Le couple du vecteur position estimé et la matrice de covariance estimée (x_k|k , p_k|k)
    """
    # Données utiles au filtrage kalman
    sigma_q = 10.  # Ecart type du modèle, on peut à priori le garder à 1, à tester
    sigma_angle = 5  # Ecart type sur la mesure de l'angle (on peut à priori la supposer nulle dans notre cas)
    sigma_distance = 10.  # Ecart type sur la mesure de la distance (à mesurer)
    te = 10 * te
    f = array([[1, te, 0, 0],
               [0, 1, 0, 0],
               [0, 0, 1, te],
               [0, 0, 0, 1]])

    q = sigma_q * array([[(te ** 3) / 3, (te ** 2) / 2, 0, 0],
                        [(te ** 2) / 2, te, 0, 0],
                        [0, 0, (te ** 3) / 3, (te ** 2) / 2],
                        [0, 0, (te ** 2) / 2, te]])

    r = array([[sigma_angle ** 2, 0],
               [0, sigma_distance ** 2]])

    h = array([[1, 0, 0, 0], [0, 0, 1, 0]])

    y_k = array([y_k[1]*cos(y_k[0]), y_k[1]*sin(y_k[0])])

    # prediction: passage de x_k|k, p_k|k à x_k+1|k, p_k+1|k
    x_predit = f.dot(x_kalm_prec)  # Etat prédit
    p_predit = f.dot(p_kalm_prec).dot(f.T) + q  # Estimation prédite de la covariance

    # mise à jour: passage de x_k+1|k, p_k+1|k à x_k+1|k+1, p_k+1|k+1
    k = p_predit.dot(h.T).dot(inv(h.dot(p_predit).dot(h.T) + r))  # Gain de Kalman optimal
    x_kalm = x_predit + k.dot(y_k - h.dot(x_predit))  # Etat mis à jour
    p_kalm = (eye(4) - k.dot(h)).dot(p_predit)  # Mise à jour de la covariance

    return x_kalm, p_kalm
