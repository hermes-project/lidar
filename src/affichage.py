#!/usr/bin/env python3
# coding: utf-8
import pylab as pl
import configparser
from math import pi

# Recuperation de la config
config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")
distance_max_x_cartesien = int(config['DETECTION']['distance_max_x_cartesien'])
distance_max_y_cartesien = int(config['DETECTION']['distance_max_y_cartesien'])
distance_max = int(config['DETECTION']['distance_max'])


def init_affichage_cartesien():
    """
    Initialisation de l'affichage.

    """

    pl.ion()
    fig = pl.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-distance_max_x_cartesien/2, distance_max_x_cartesien/2)
    ax.set_ylim(-distance_max_y_cartesien/2, distance_max_y_cartesien/2)
    ax.axhline(0, 0)
    ax.axvline(0, 0)
    r = []
    theta = []
    ax.scatter(theta, r)

    return ax, fig


def init_affichage_polaire():
    """
    Initialisation de l'affichage.

    """

    pl.ion()
    fig = pl.figure()
    ax = fig.add_subplot(111, polar=True)  # polaire !
    ax.set_ylim(0, distance_max)
    ax.set_ylim(0, 2 * pi)
    ax.axhline(0, 0)
    ax.axvline(0, 0)
    r = []
    theta = []
    ax.scatter(theta, r)

    return ax, fig
