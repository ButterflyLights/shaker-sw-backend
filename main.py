import numpy as np
import sounddevice as sd
import signal_generators as sg

SAMPLING_RATE = 44100
FREQ = 440
AMPLITUDE = .1

start_idx = 0

def callback(outdata, frames, time, status):
    if status:
        print(status)
    global start_idx
    t = (start_idx + np.arange(frames)) / SAMPLING_RATE
    t = t.reshape(-1, 1)
    outdata[:] = sg.sin(t, AMPLITUDE, FREQ).reshape(-1, 1)
    start_idx += frames

def play():
    with sd.OutputStream(device=sd.default.device, channels=1, callback=callback,
                        samplerate=SAMPLING_RATE):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()

play()