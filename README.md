# LiDAR
Code of data treatment of the Hermes-LiDAR project.

# Installation
1) Clone the repository.
2) sudo pip install pyserial
3) sudo pip install matplotlib
4) Install tk8.6 (yaourt -S tk).
5) Enjoy !

# Choice of application
You can:
- either show the obstacles on the screen ("hl_connected = False" in config.ini)
- either connect with a java server that has launched the python main.py before ("hl_connected = True" in config.ini)

# TODO

- [x] Détection et affichage des obstacles
- [x] Kalman
- [x] Communication socket avec le HL Java
- [x] Fichiers de log
- [ ] Résoudre problème de "Cleaning buffer..."
- [ ] Arrêt propre (Tk, thread et fermeture série)
