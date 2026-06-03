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

eventStartedPlayback = threading.Event()
eventFinishedPlayback = threading.Event()
    
class MeasurementState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"

def getState():
    if not eventStartedPlayback.is_set() and not eventFinishedPlayback.is_set():
        return MeasurementState.IDLE

    elif eventStartedPlayback.is_set() and not eventFinishedPlayback.is_set():
        return MeasurementState.RUNNING

    else:
        return MeasurementState.FINISHED

def genSignal(data):
    if data["signalType"] == "audioFile":
        signal, samplerate = sf.read("../data/audioFiles/" + data["signalParams"]["filename"], always_2d=True)
        signal = np.array([[i/samplerate, (signal[i][0] + signal[i][1]) / 2] for i in range(len(signal))])

    elif data["signalType"] == "sine":
        signal = sg.sin(**data["signalParams"])
        samplerate = config.configData["audioSamplerate"]

    elif data["signalType"] == "sweep":
        signal = sg.sineSweep(**data["signalParams"])
        samplerate = config.configData["audioSamplerate"]

    elif data["signalType"] == "random":
        signal = sg.whiteNoise(**data["signalParams"])
        samplerate = config.configData["audioSamplerate"]

    return signal, samplerate

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
    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    print(data)

    # build system input signal depending on data and start measurement
    u, samplerate = genSignal(data)
    measure(u, samplerate)

def runTest():
    eventStartedPlayback.clear()
    eventFinishedPlayback.clear()

    with open("testMsg_audio-file.json") as f:
        data = json.load(f)

    # build system input signal depending on data and start measurement
    u, samplerate = genSignal(data)
    measure(u, samplerate)

if __name__ == "__main__":
    runTest()