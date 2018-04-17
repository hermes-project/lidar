from numpy import array, eye, set_printoptions
from math import atan2, sqrt, pi
from numpy.linalg import inv

set_printoptions(suppress=True)


def ekf(Te, y_k, x_kalm_prec, p_kalm_prec):
    # print("KAAAAAALLLLLMMMMMMAAAANNNN")
    # print("Te ", Te)
    # print("y_k ", y_k)
    # print("x_kalm_prec ", x_kalm_prec)
    # print("p_kalm_prec ", p_kalm_prec)

    """
    Extended Kalman Filter:
    Applique le filtre de kalman éendu, fournissant la position estimée x_k|k,
    à partir de la mesure y_k et la position estimée précédente x_k-1|k-1
    Met aussi à jours la matrice de covariances estimée

    :param y_k: Le vecteur des mesures, sous la forme numpy.array([angle,distance])
    :param x_kalm_prec: Le vecteur position estimée précédent x_k-1|k-1, sous la forme numpy.array([x,vitesse_x,y,vitesse_y])
    :param p_kalm_prec: La matrice de covariance précédente p_k-1|k-1, sous la forme d'un array numpy de taille 4x4,
    initialement c'est la matrice identité (numpy.eye(4))
    :return: x_kalm, p_kalm: Le couple du vecteur position estimé et la matrice de covariance estimée (x_k|k , p_k|k)
    """
    # TODO: F et Q dépendent du temps d'échantillonnage, et R dépend des variances de mesures -> gérer ça

    # Données utiles au filtrage kalman
    sigmaQ = 10.  # Ecart type du modèle, on peut à priori le garder à 1, à tester
    sigma_angle = pi / 360  # Ecart type sur la mesure de l'angle (on peut à priori la supposer nulle dans notre cas)
    sigma_distance = 300.  # Ecart type sur la mesure de la distance (à mesurer)

    F = array([[1, Te, 0, 0],
               [0, 1, 0, 0],
               [0, 0, 1, Te],
               [0, 0, 0, 1]])

    Q = sigmaQ * array([[(Te ** 3) / 3, (Te ** 2) / 2, 0, 0],
                        [(Te ** 2) / 2, Te, 0, 0],
                        [0, 0, (Te ** 3) / 3, (Te ** 2) / 2],
                        [0, 0, (Te ** 2) / 2, Te]])

    R = array([[sigma_angle ** 2, 0],
               [0, sigma_distance ** 2]])

    # PREDICTION: passage de x_k|k, p_k|k à x_k+1|k, p_k+1|k
    x_predit = F.dot(x_kalm_prec)  # Etat prédit
    p_predit = F.dot(p_kalm_prec).dot(F.T) + Q  # Estimation prédite de la covariance

    # Valeurs en x et y des positions prédites
    x = x_predit[0]
    y = x_predit[2]

    # LINEARISATION des mesures autour du point prédit:(cf Taylor)
    # Valeurs en a=x_predit des deux fonctions f et g
    f_a = atan2(y, x)
    g_a = sqrt((x ** 2) + (y ** 2))

    # Gradients de f et g
    diff_x_g = x / f_a
    diff_y_g = y / f_a
    diff_x_f = -y / ((x ** 2) + (y ** 2))
    diff_y_f = x / ((x ** 2) + (y ** 2))

    y_a = [f_a, g_a]

    H = array([[diff_x_f, 0, diff_y_f, 0], [diff_x_g, 0, diff_y_g, 0]]) # Jacobien

    #Gain de kalman
    K = p_predit.dot(H.T).dot(inv(H.dot(p_predit).dot(H.T) + R))
    y_k = y_k - y_a + H.dot(x_predit)                   # Innovation

    # MISE A JOUR: passage de x_k+1|k, p_k+1|k à x_k+1|k+1, p_k+1|k+1
    x_kalm = x_predit + K.dot(y_k - H.dot(x_predit))    # Etat estimé mis à jour
    p_kalm = (eye(4) - K.dot(H)).dot(p_predit)          # Matrice de covariance estimée mise à jour

    return x_kalm, p_kalm
