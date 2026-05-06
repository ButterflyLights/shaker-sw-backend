import numpy as np
import sounddevice as sd

SAMPLING_RATE = 44100

start_idx = 0

def play(generator, amplitude, freq=0):
    def callback(outdata, frames, time, status):
        if status:
            print(status)
        global start_idx
        t = (start_idx + np.arange(frames)) / SAMPLING_RATE
        t = t.reshape(-1, 1)
        outdata[:] = generator(t, amplitude, freq).reshape(-1, 1)
        start_idx += frames
    
    with sd.OutputStream(device=sd.default.device, channels=1, callback=callback,
                        samplerate=SAMPLING_RATE):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()