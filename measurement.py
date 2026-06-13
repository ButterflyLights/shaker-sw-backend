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
import files

eventStartedPlayback = threading.Event()
eventFinishedPlayback = threading.Event()

class MeasurementState(str, Enum):
    IDLE = "idle"
    GENERATING_SIGNAL = "generating signal"
    SAVING_FILES = "saving files"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"

state = MeasurementState.IDLE

def getState():
    return state

class Measurement:
    def __init__(self, command):
        self.command = command
        self.id = None

    def _downsample(self, data, factor=config.configData["dataDownsamplingFactor"]):
        downsampled = []
        for i in range(len(data)):
            if i % factor == 0:
                downsampled.append(data[i])
        return downsampled

    def setupMeasurementFiles(self):
        global state

        state = MeasurementState.SAVING_FILES

        # insert entry into measurements table
        measurementsTable = database.Table(config.configData["dbMeasurementsTable"])
        self.id = measurementsTable.insert(profileId=self.command["profileId"])
        if self.id == False: return False

        # generate file path
        path = f"{config.configData["dataWorkingDir"]}{config.configData["dataMeasurementPath"]}{self.id}"

        measurementsTable.updateId(self.id, path=path)

        if os.path.exists(path):
            print("measurement path already exists")
            state = MeasurementState.ERROR
            return False

        os.makedirs(path)

        # generate input files
        
        with open(f"{path}/metadata.json", 'w+') as f:
            data = {
                "command": self.command,
                "samplerate": self.signal["samplerate"],
                "downsamplingFactor": config.configData["dataDownsamplingFactor"],
            }

            json.dump(data, f, indent=4)

        files.writeFile(f"{path}/t.bin", np.transpose(self.signal["uAcc"])[0])
        files.writeFile(f"{path}/uAcc.bin", np.transpose(self.signal["uAcc"])[1])
        files.writeFile(f"{path}/uDisp.bin", np.transpose(self.signal["uDisp"])[1])

        # TODO: write downsampled data?

        files.writeFile(f"{path}/f.bin", np.transpose(self.psdAcc)[0]) # TODO: fAcc == fDisp???
        files.writeFile(f"{path}/psdAcc.bin", np.transpose(self.psdAcc)[1])
        files.writeFile(f"{path}/psdDisp.bin", np.transpose(self.psdDisp)[1])

    def saveMeasurement(self, data):
        global state

        state = MeasurementState.SAVING_FILES

    def genSignal(self):
        global state

        state = MeasurementState.GENERATING_SIGNAL

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
        if self.signal == False:
            state = MeasurementState.ERROR
            return False

        self.psdAcc = filters.psd(np.transpose(self.signal["uAcc"])[1], self.signal["samplerate"])
        self.psdDisp = filters.psd(np.transpose(self.signal["uDisp"])[1], self.signal["samplerate"])

        # plt.loglog(np.transpose(self.psdAcc)[0], np.transpose(self.psdAcc)[1])
        # plt.grid()
        # plt.show()

        return self.signal["uDisp"], self.signal["samplerate"]

def targetPlayer(p, signal, samplerate):
    p.play(signal, samplerate)

def targetMeasurement():
    global state
    # start measurement when playback starts
    eventStartedPlayback.wait()
    state = MeasurementState.RUNNING

    # collect data from DAQ

    # stop measurement when playback stops
    eventFinishedPlayback.wait()

    # save measurement data with measurement object

def measure(u, samplerate):
    global state
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

    state = MeasurementState.FINISHED

def run(data):
    global state
    
    state = MeasurementState.IDLE

    m = Measurement(data)

    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    print(data)

    # build system input signal depending on data and start measurement
    if state != MeasurementState.ERROR:
        signal = m.genSignal()
        if signal != False: (u, samplerate) = signal

    if state != MeasurementState.ERROR: m.setupMeasurementFiles()

    if state != MeasurementState.ERROR: measure(u, samplerate)

def runTest():
    global state

    state = MeasurementState.IDLE

    with open("testMsg_random.json") as f:
        data = json.load(f)
    
    m = Measurement(data)

    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    # build system input signal depending on data and start measurement
    if state != MeasurementState.ERROR:
        signal = m.genSignal()
        if signal != False: (u, samplerate) = signal

    # if state != MeasurementState.ERROR: measure(u, samplerate)
    
if __name__ == "__main__":
    runTest()

    # m = Measurement({"asdf"})
    # print(m._downsample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], factor=3))