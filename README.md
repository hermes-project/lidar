# LiDAR
Code of data treatment of the Hermes-LiDAR project.

# Installation
0) Use Python 3
1) Clone the repository.
2) sudo pip install pyserial
3) sudo pip install matplotlib
4) Install tk8.6 (sudo pacman -S tk or sudo apt-get install tk).
5) Enjoy !

# Choice of application
You can:
- either show the obstacles on the screen ("hl_connected = False" in config.ini)
- either connect with a java server that has launched the python main.py before ("hl_connected = True" in config.ini)

# TODO
- [x] Detect and display obstacles
- [x] Kalman filter implementation
- [x] Sockets for communication with the Java high-level
- [x] Logging
- [ ] Solve "Cleaning buffer..." issue with rplidar
- [ ] Cleaner shutdown(Tk, thread, serial errors when stopping)
