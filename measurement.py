import threading
import numpy as np
import player
import signal_generators as sg
import filters
import matplotlib.pyplot as plt
import socket
import json
from enum import Enum
import soundfile as sf
import os
import config
import database

eventStartedPlayback = threading.Event()
eventFinishedPlayback = threading.Event()
    
class MeasurementState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"

class Measurement:
    def __init__(self, command):
        self.command = command
        self.uFilename = None
        self.yFilename = None
        self.id = None

    def setupMeasurementFiles(self):
        # insert entry into measurements table
        measurementsTable = database.Table(config.configData["dbMeasurementsTable"])
        self.id = measurementsTable.insert(profileId=self.command["profileId"])
        # TODO: dont start measurement if sql fails / set error

        print("id:", self.id)

        # generate file paths
        path = f"../data/measurements/{self.id}"
        self.uFilename = f"{path}/u.json"
        self.yFilename = f"{path}/y.json"

        if os.path.exists(path):
            # TODO: set error
            print("measurement path already exists")
            return

        else:
            os.makedirs(path)

        # generate input file
        with open(self.uFilename, 'w+') as file:
            t = np.transpose(self.signal["uAcc"])[0]
            u = np.transpose(self.signal["uAcc"])[1]
            f = np.transpose(self.psdAcc)[0]
            psd = np.transpose(self.psdAcc)[1]

            data = {
                "command": self.command,
                "samplerate": self.signal["samplerate"],
                "t": list(t),
                "u": list(u),
                "f": list(f),
                "psd": list(psd)
            }

            json.dump(data, file)

    def saveMeasurement(self, data):
        pass

    def genSignal(self):
        if self.command["signalType"] == "audioFile":
            sg.convertToDisp = False
            generator = sg.audioFile

        elif self.command["signalType"] == "sweep":
            sg.convertToDisp = True
            generator = sg.sineSweep

        elif self.command["signalType"] == "random":
            sg.convertToDisp = True
            generator = sg.whiteNoise

        self.signal = generator(**self.command["signalParams"])
        self.psdAcc = filters.psd(np.transpose(self.signal["uAcc"])[1])

        # plt.semilogy(np.transpose(self.psdAcc)[0], np.transpose(self.psdAcc)[1])
        # plt.show()

        return self.signal["uDisp"], self.signal["samplerate"]

def getState():
    if not eventStartedPlayback.is_set() and not eventFinishedPlayback.is_set():
        return MeasurementState.IDLE

    elif eventStartedPlayback.is_set() and not eventFinishedPlayback.is_set():
        return MeasurementState.RUNNING

    else:
        return MeasurementState.FINISHED

def targetPlayer(p, signal, samplerate):
    p.play(signal, samplerate)

def targetMeasurement():
    # start measurement when playback starts
    eventStartedPlayback.wait()

    # collect data from DAQ

    # stop measurement when playback stops
    eventFinishedPlayback.wait()

    # save measurement data with measurement object

def measure(u, samplerate):
    p = player.Player(eventStartedPlayback, eventFinishedPlayback)

    # init threads
    threads = []
    playerThread = threading.Thread(target=targetPlayer, args=(p, u, samplerate,))
    measurementThread = threading.Thread(target=targetMeasurement)
    threads.append(playerThread)
    threads.append(measurementThread)

    # wait for threads to join
    for t in threads: t.start()
    for t in threads: t.join()

def run(data):
    m = Measurement(data)

    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    print(data)

    # build system input signal depending on data and start measurement
    u, samplerate = m.genSignal()
    m.setupMeasurementFiles()
    measure(u, samplerate)

def runTest():
    with open("testMsg_random.json") as f:
        data = json.load(f)
    
    m = Measurement(data)

    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    # build system input signal depending on data and start measurement
    u, samplerate = m.genSignal()
    measure(u, samplerate)

if __name__ == "__main__":
    runTest()