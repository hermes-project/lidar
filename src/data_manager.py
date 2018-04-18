from rplidar import RPLidar
from time import sleep, time
from csv import writer, reader


def scanData(lidar, seconds=10, turns=0):
    """
    Returns data from lidar scans
    :param lidar: The rplidar.RPLidar lidar to use
    :param seconds: number of seconds of scan to do
    :param turns: number of turns to do
    :return:
    """
    measureData = []

    lidar.start_motor()
    sleep(3)  # Attente de la prise de vitesse du lidar
    lidar.start()
    turn = 0
    if seconds == 0 and turns == 0:
        seconds = 10

    startTime = time()

    newTurnOld = False

    for measure in lidar.iter_measures():
        measureData.append(measure)
        if measure[0] and not newTurnOld:
            turn += 1
            if turns != 0 and turn == turns:
                return measureData
        if turns == 0 and time() - startTime > seconds:
            return measureData


def saveData(path, dataToSave):
    """
    S'occupe de sauvegarder des mesures dans un fichier .csv au format NEW_TURN,QUALITY,ANGLE,DISTANCE
    :param path: chemin vers le fichier où enregistrer les donnees
    :param dataToSave: liste de scans(tours entiers)
    """
    with open(path, "w") as file:
        csvWriter = writer(file, delimiter=",")
        for measure in dataToSave:
            csvWriter.writerow([measure[0]] + [measure[1]] + [measure[2]] + [measure[3]])


def readData(path):
    """
    recupere les donnees d'un fichier .csv au format NEW_TURN,QUALITY,ANGLE,DISTANCE
    :param path:
    """
    dataToReturn = []
    with open(path, "r") as file:
        csvReader = reader(file, delimiter=",")
        for row in csvReader:
            dataToReturn.append([row[0] == "True", int(row[1]), float(row[2]), float(row[3])])
    return dataToReturn


if __name__ == '__main__':
    NB_TOURS = 0
    NB_SECONDES = 10

    FILE_PATH = "./scanData.csv"
    # lidar=RPLidar("/dev/ttyUSB0")
    data = []  # scanData(lidar,NB_SECONDES,NB_TOURS)
    print(data)
    saveData(FILE_PATH, data)
