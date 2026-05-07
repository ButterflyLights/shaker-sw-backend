import numpy as np
import sounddevice as sd
import threading

SAMPLERATE = 44100

event = threading.Event()
start_idx = 0

def play(generator, **kwargs):
    def callback(outdata, frames, time, status):
        if status:
            print(status)
        global start_idx
        t = (start_idx + np.arange(frames)) / SAMPLERATE
        t = t.reshape(-1, 1)
        outdata[:] = generator(event, t, **kwargs).reshape(-1, 1)
        start_idx += frames
    
    with sd.OutputStream(device=sd.default.device, channels=1, callback=callback,
                        samplerate=SAMPLERATE, finished_callback=event.set):
        event.wait()
        print("playback finished")
        # print('#' * 80)
        # print('press Return to quit')
        # print('#' * 80)
        # input()