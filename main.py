import threading
import time
import numpy as np
import player
import signal_generators as sg
import matplotlib.pyplot as plt

sweepArgs = {"amplitude": 0.01, "freqStart": 100, "freqEnd": 1000, "sweepRate": 1/2}

eventStart = threading.Event()
eventFinished = threading.Event()

def targetPlayer(p, signal):
    p.play(signal)
    # p.playFile("files/Barbie Girl - Aqua.wav")

def targetMeasurement():
    eventStart.wait()
    # collect data from DAQ
    eventFinished.wait()

def measure(u):
    p = player.Player(eventStart, eventFinished)

    threads = []

    playerThread = threading.Thread(target=targetPlayer, args=(p, u,))
    measurementThread = threading.Thread(target=targetMeasurement)

    threads.append(playerThread)
    threads.append(measurementThread)

    for t in threads: t.start()
    for t in threads: t.join()

def main():
    # build system input signal
    u = sg.sineSweep(**sweepArgs)

    # measure
    measure(u)

if __name__ == "__main__":
    main()