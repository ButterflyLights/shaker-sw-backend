import threading
import numpy as np
import player
import signal_generators as sg
import matplotlib.pyplot as plt
import socket
import json
from enum import Enum
import soundfile as sf
import config
import database

eventStartedPlayback = threading.Event()
eventFinishedPlayback = threading.Event()
    
class MeasurementState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"

class Measurement:
    def __init__(self, command):
        self.command = command
        self.uFilename = ""
        self.yFilename = ""

    def setupMeasurementFiles(self):
        # insert entry into measurements table
        measurementsTable = database.Table(config.configData["dbMeasurementsTable"])
        measurementsTable.insert(profileId=self.command["profileId"])

        # generate files

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

        return generator(**self.command["signalParams"])

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
    m.setupMeasurementFiles()

    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    print(data)

    # build system input signal depending on data and start measurement
    u, samplerate = m.genSignal()
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