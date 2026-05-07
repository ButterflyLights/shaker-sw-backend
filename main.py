import threading
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
    # start measurement when playback starts
    eventStart.wait()

    # collect data from DAQ

    # stop measurement when playback stops
    eventFinished.wait()

def measure(u):
    p = player.Player(eventStart, eventFinished)

    # init threads
    threads = []
    playerThread = threading.Thread(target=targetPlayer, args=(p, u,))
    measurementThread = threading.Thread(target=targetMeasurement)
    threads.append(playerThread)
    threads.append(measurementThread)

    # wait for threads to join
    for t in threads: t.start()
    for t in threads: t.join()

def main():
    # build system input signal

    # u = sg.sineSweep(**sweepArgs)
    # f = sg.sineSweepFreq(np.transpose(u)[0], sweepArgs["freqStart"], sweepArgs["freqEnd"], sweepArgs["sweepRate"])

    # plt.plot(np.transpose(u)[0], f)
    # plt.show()

    u = sg.square(5, 0.01, 440)

    # measure
    measure(u)

if __name__ == "__main__":
    main()