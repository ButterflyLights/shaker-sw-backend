import numpy as np
import sounddevice as sd
import threading
import soundfile as sf

SAMPLERATE = 44100

event = threading.Event()
start_idx = 0
current_frame = 0

class Player:
    def __init__(self):
        self.t = 0
        self.playing = False

    def play(self, generator, **kwargs):
        def callback(outdata, frames, time, status):
            global start_idx
            if status:
                print(status)
            t = (start_idx + np.arange(frames)) / SAMPLERATE
            self.t = t
            t = t.reshape(-1, 1)
            outdata[:] = generator(event, t, **kwargs).reshape(-1, 1)
            start_idx += frames
        
        stream = sd.OutputStream(device=sd.default.device, channels=1, callback=callback,
                            samplerate=SAMPLERATE, finished_callback=event.set)

        with stream:
            self.playing = True
            event.wait()
            print("playback finished")
            self.playing = False

    def playFile(self, filename, amplitude):
        data, fs = sf.read(filename, always_2d=True)

        def callback(outdata, frames, time, status):
            global current_frame
            if status:
                print(status)
            chunksize = min(len(data) - current_frame, frames)

            tmp = data[current_frame:current_frame + chunksize]
            # stereo -> mono
            if tmp.shape[1] == 2:
                tmp = np.array([np.array([(s[0] + s[1]) / 2]) for s in tmp])
          
            outdata[:chunksize] = amplitude * tmp
            if chunksize < frames:
                outdata[chunksize:] = 0
                raise sd.CallbackStop()
            current_frame += chunksize

        stream = sd.OutputStream(
            samplerate=fs, device=sd.default.device, channels=1,
            callback=callback, finished_callback=event.set)

        with stream:
            event.wait()
            print("playback finished")