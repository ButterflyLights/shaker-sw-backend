import threading
import numpy as np
import player
import signal_generators as sg
import matplotlib.pyplot as plt
import socket
import json
import soundfile as sf
import config

eventStartMeasurement = threading.Event()
eventStartedPlayback = threading.Event()
eventFinishedPlayback = threading.Event()
    
def genSignal(data):
    if data["signalType"] == "audio-file":
        signal, samplerate = sf.read(data["signalParams"]["filename"], always_2d=True)
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

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((config.configData["backendHost"], config.configData["backendPort"]))
        print(f"...listening on port {config.configData["backendPort"]}")
        sock.listen(1)
        conn, addr = sock.accept()

        with conn:
            print(f"Connected by {addr}")
            while True:
                # wait for start msg
                msg = conn.recv(1024)
                data = json.loads(msg)

                # build system input signal depending on data and start measurement
                u, samplerate = genSignal(data)
                measure(u, samplerate)

                # send done msg
                conn.sendall(msg)

                # TODO: check if connection is still active?

def runTest():
    # test
    with open("testMsg_random.json") as f:
        data = json.load(f)

    # build system input signal depending on data and start measurement
    u, samplerate = genSignal(data)
    measure(u, samplerate)

if __name__ == "__main__":
    runTest()