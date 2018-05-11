
import numpy as np
from math import sqrt
import collections
import scipy.linalg
from scipy.stats import norm

___author__ = "Clément Besnier"


class UnscentedKalman:
    """
    Cette classe implémente l'algorithme du Filitrage de Kalman Unscented
    Source : Machine Learning a probabilistic perspective p. 651-652
    """
    def __init__(self, mu0, SIGMA0, Q, R, d, alpha, beta, kappa, dt):
        """
        g est la fonction qui associe la position en t à la position en t+1
        h est la fonction qui associe la position réelle aux mesures correspondantes
        mu0 est la position initiale du robot
        SIGMA est la matrice de covariance initiale

        """
        self.dt = dt
        self.d = d  # c'est la dimension de l'espace cachée
        self.alpha = float(alpha) # paramètre bizarre
        self.beta = float(beta)  # paramètre bizarre
        self.kappa = kappa  # paramètre bizarre
        self.mu = mu0  # position initiale
        self.SIGMA = SIGMA0  # variance initiale
        self.lam = alpha* * 2 *( d +kappa) - d  # un paramètre un peu étrange aussi
        self.gamma = d+ self.lam  # à nouveau bizarre !
        self.Q = Q  # matrice de covariance de la gaussienne de l'équation d'évolution
        self.R = R  # matrice de covariance de la gaussienne de l'équation d'observation

        # calculs de coefficients
        self.wm0 = float(self.lam) / (self.d + self.lam)
        self.wm = 1 / (2. * (self.d + self.lam))  # wm = wc (wc non implémenté)
        self.wc0 = self.wm0 + (1 - self.alpha ** 2 + self.beta)

    def _first_step(self):
        """
        Estimation de mu_barre et de sigma_barre à partir de l'itération précédente
        """
        # first Unscented transform
        racine_sigma = np.asmatrix(scipy.linalg.sqrtm(self.gamma * self.SIGMA))
        # self.mu = self.mu.T
        # print self.mu
        # print racine_sigma[:, 0]
        # print "racine carrée", racine_sigma
        # print "mu", self.mu, "racine_sigma", racine_sigma.shape, racine_sigma[:, 1].shape
        # print "self.mu - self.gamma*racine_sigma[:, i]", self.mu - self.gamma*racine_sigma[:, 1]
        self.points_sigma = [self.mu]
        self.points_sigma.extend([self.mu - racine_sigma[:, i] for i in range(0, self.d)])  # de -1 à - self.d
        self.points_sigma.extend([self.mu + racine_sigma[:, i] for i in range(0, self.d)])  # de 1 à self.d

        # print "self.points_sigma", len(self.points_sigma), np.array(self.points_sigma).shape
        # self.points_sigma = np.array(self.points_sigma)
        # self.z_etoile_barre = np.array([self.g(self.points_sigma[i]).reshape((4,)) for i in range(0, 2*self.d)])

        self.z_etoile_barre = []  # np.asmatrix(np.zeros(self.points_sigma.shape))
        # print len(self.points_sigma)
        for i in range(len(self.points_sigma)):
            self.z_etoile_barre.append(self.g(self.points_sigma[i]))
            # self.z_etoile_barre[i,:] = self.g(self.points_sigma[i])

        self.mu_barre = self.wm0 * self.z_etoile_barre[0]

        # print "mu_barre", self.mu_barre.shape
        # print self.mu_barre
        # print self.z_etoile_barre[2]
        # print self.wm
        for i in range(1, len(self.z_etoile_barre)):
            # print i
            # print "self.wm*self.z_etoile_barre[i]", (self.wm*self.z_etoile_barre[i]).shape
            self.mu_barre += self.wm * self.z_etoile_barre[i]

        # calcul de SIGMA_barre
        # print "mu barre", self.mu_barre.shape
        # print "z_etoile_barre", len(self.z_etoile_barre), len(self.z_etoile_barre[0]), self.z_etoile_barre[0], self.mu_barre
        self.SIGMA_barre = self.wc0 * np.dot((self.z_etoile_barre[0] - self.mu_barre),
                                             (self.z_etoile_barre[0] - self.mu_barre).T)
        for i in range(1, len(self.z_etoile_barre)):
            self.SIGMA_barre += self.wm * np.dot((self.z_etoile_barre[i] - self.mu_barre),
                                                 (self.z_etoile_barre[i] - self.mu_barre).T)
        # print "SIGMA_barre", self.SIGMA_barre.shape
        self.SIGMA_barre += self.Q

    def _second_step(self, y):
        """
        y est la mesure à l'instant t
        Estimation de mu et de sigma présent
        """
        # second unscented transform
        racine_sigma_barre = np.asmatrix(scipy.linalg.sqrtm(self.SIGMA_barre))
        self.points_sigma_barre = [self.mu_barre] + \
                                  [self.mu_barre - sqrt(self.gamma) * racine_sigma_barre[:, i] for i in
                                   range(0, self.d)] + \
                                  [self.mu_barre + sqrt(self.gamma) * racine_sigma_barre[:, i] for i in
                                   range(0, self.d)]
        # print "points_sigma_barre", self.points_sigma_barre
        self.y_etoile_barre = [self.h(self.points_sigma_barre[i]) for i in range(0, len(self.points_sigma_barre))]

        self.y_chapeau = self.wm0 * self.y_etoile_barre[0]
        for i in range(1, len(self.y_etoile_barre)):
            self.y_chapeau += self.wm * self.y_etoile_barre[i]
        # Calcul de S
        self.S = self.wc0 * np.dot(self.y_etoile_barre[0] - self.y_chapeau,
                                   (self.y_etoile_barre[0] - self.y_chapeau).T)
        for i in range(1, len(self.y_etoile_barre)):
            self.S += self.wm * np.dot(self.y_etoile_barre[i] - self.y_chapeau,
                                       (self.y_etoile_barre[i] - self.y_chapeau).T)
        # print "S", self.S.shape
        self.S += self.R
        # calcul de SIGMA_z_y
        self.SIGMA_z_y_barre = self.wc0 * np.dot((self.z_etoile_barre[0] - self.mu_barre),
                                                 (self.y_etoile_barre[0] - self.y_chapeau).T)
        for i in range(1, len(self.z_etoile_barre)):
            self.SIGMA_z_y_barre += self.wm * np.dot(self.z_etoile_barre[i] - self.mu_barre,
                                                     (self.y_etoile_barre[i] - self.y_chapeau).T)
        self.K = np.dot(self.SIGMA_z_y_barre, scipy.linalg.inv(self.S))
        # print "K", self.K.shape, "y", y.shape
        # Les valeurs qui nous interessent
        self.mu = self.mu_barre + np.dot(self.K, y - self.y_chapeau)
        self.SIGMA = self.SIGMA_barre - np.dot(np.dot(self.K, self.S), self.K.T)

    def filter(self, y):
        """
        On sépare les deux pas parce que l'un a besoin d'une mesure tandis que l'autre non
        :param y: c'est la mesure provenant du capteur
        """
        self._first_step()
        if y is None:  # aucune mesure
            self._second_step(self.mu)  # pour l'instant, c'est une proposition, on pourra trouver mieux
        else:
            self._second_step(y)

    def g(self, x, dim=2):
        """
        Pour notre modélisation, on choisit comme vecteur x = [abscisse de la position,
        ordonnée de la position] ou [abscisse de la position,
        ordonnée de la position, abscisse de la vitesse, ordonnées de la vitesse]
        """
        # if dim == 2:
        #     F = np.matrix([[1., 0.], [0., 1.]])
        # elif dim == 3:
        #     F = np.matrix([[1., 0, 0], [0., 1., 0.], [0., 0., 1.]])
        # else: #dim == 4
        #     F = np.matrix([[1., 0., self.dt, 0.], [0., 1., 0., self.dt], [0., 0., 1., 0.], [0., 0., 0., 1.]])
        # print F.shape, x.shape
        F = np.matrix([[1., 0.], [0., 1.]])
        res = np.dot(F, x)
        # print res.shape
        return res

    def h(self, x):
        """
        La fonction renvoie les données comme si elles ont été mesurées.
        """
        # print "x shape", x.shape
        measures = x[0], x[1]
        return np.asmatrix(measures).T  # [:,np.newaxis]

    def get_state(self):
        """
        self.mu est la position moyenne
        """
        return self.mu


# classe à arranger pour le Kalman Unscented
class UnscentedKalmanFilter:

    def __init__(self, x0, dt, coeff_s=100, coeff_q=0.00001, coeff_r=0.1, dime=2):
        """
        x0 est un array(x,y) ou array(x,y,x point, y point)
        """
        self.dt = dt
        # x = np.array(x).T
        mu0 = x0
        d = 2
        kappa = 2
        alpha = 1
        beta = 0

        # x = np.array([1400,100,0.,0.])[:, np.newaxis] # vecteur d'état au départ
        # if dime == 2:
        #     SIGMA0 = np.matrix([[0.001, 0.], [0., 0.001]])
        #     R = np.matrix([[90, 0., 0.], [0., 90, 0.], [0., 0., 90]])  #dimension de la matrice égale au nombre de dimensions des mesures !
        #     Q = np.matrix([[self.dt**3/3., 0, self.dt**2/2., 0],[0, self.dt**3/3., 0, self.dt**2/2],
        #                   [self.dt**2/2., 0, 4*self.dt, 0], [0, self.dt**2/2, 0, 4*self.dt]])
        # else:
        # SIGMA0 = np.matrix([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]) # incertitude initiale
        SIGMA0 = np.eye(2)
        SIGMA0 *= coeff_s
        R = np.eye(3)
        # R = np.matrix([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])  #dimension de la matrice égale au nombre de dimensions des mesures !
        R *= coeff_r

        # Q = np.matrix([[self.dt**3/3., self.dt**2/2., 0, 0],[self.dt**2/2.,self.dt, 0, 0],
        #            [0,0,self.dt**3/3.,self.dt**2/2],[0,0,self.dt**2/2,self.dt]])
        # Q *= 20;
        Q = np.eye(2)
        # Q = np.matrix([[1., 0, 0, 0],[0, 1, 0, 0],
        #                [0, 0, 1, 0],[0, 0, 0, 1]])
        # Q = np.matrix([[self.dt**3/3., 0, self.dt**2/2., 0],[0, self.dt**3/3., 0, self.dt**2/2],
        #                [self.dt**2/2., 0, 4*self.dt, 0], [0, self.dt**2/2, 0, 4*self.dt]])
        # Q = np.matrix([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 4, 0],[0, 0, 0, 4]])
        Q *= coeff_q  # (1-0.98**2)

        self.ukf = UnscentedKalman(mu0, SIGMA0, Q, R, d, alpha=alpha, beta=beta, kappa=kappa, dt=dt)
        self.historique = collections.deque(maxlen=3)
        self.valeurs_rejetees = 0
        self.acceleration = None

    def get_state(self):
        """

        :return: the state of the robot
        """
        return self.ukf.mu

    def update_dt(self, new_dt):
        """
        Modifie la période d'échantillonage
        """
        self.dt = new_dt
        self.ukf.F[0, 2] = new_dt
        self.ukf.F[1, 3] = new_dt

    def get_state_position(self):
        """

        :return: a Point
        """
        state = self.ukf.mu
        # print state
        return float(state[0]), float(state[1])

    def get_state_velocity(self):
        """

        :return: a Velocity
        """
        state = self.ukf.mu
        return float(state[2]), float(state[3])

    def update(self, y):
        """
        Je ne sait pas si c'est vraiement utilse
        fonction qui est utilisé à chaque mesure
        y est un vecteur de mesure de dimension 4 : (x, y, x point, y point)
        """

        # if self._filtrage_acceleration(Point(x, y)):
        #    self.last_point = Point(x, y)
        self.ukf.filter(y)
        pos_filtre = self.ukf.get_state()
        #    self.filtre_kalman.measurement(np.array([x,y])[:, np.newaxis])
        self.historique.append(self.ukf.get_state())
        # print y, pos_filtre[0], pos_filtre[1]
        # else:
        #    self.last_point = None
        return pos_filtre
        #    self.filtre_kalman.prediction()

    def _acceleration_filtering(self, pointm0):
        """
        Vérifie si le point est cohérent avec la position actuelle, en basant sur l'accélération
        """
        # Pas suffisamment de valeurs précédentes pour calculer l'accélération
        if len(self.historique) != 3:
            return True

        # 3 derniers points valides
        pointm1 = self.historique[2]
        pointm2 = self.historique[1]
        pointm3 = self.historique[0]

        # Vecteurs vitesses et accélération
        vitesse_actuelle = pointm0 - pointm1
        vitesse_m1 = pointm1 - pointm2
        vitesse_m2 = pointm2 - pointm3
        acceleration_actuelle = vitesse_actuelle - vitesse_m1
        acceleration_precedente = vitesse_m1 - vitesse_m2
        jerk = acceleration_actuelle - acceleration_precedente

        # Produit scalaire pour savoir s'il y a accélération ou décélération
        produit = acceleration_actuelle.x * vitesse_m1.x + acceleration_actuelle.y * vitesse_m1.y

        # Rejette les accélérations brutales
        if acceleration_actuelle.norme() / self.dt ** 2 > 50000 and self.valeurs_rejetees < 3:
            # ~ print("accélération = {0}, produit = {1}, jerk = {2}".format(acceleration_actuelle.norme() / self.dt**2, produit, jerk.norme() / self.dt**3))
            self.valeurs_rejetees += 1
            return False
        else:
            self.valeurs_rejetees = 0
            return True