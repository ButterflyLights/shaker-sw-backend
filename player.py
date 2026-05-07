import numpy as np
import sounddevice as sd
import soundfile as sf
import signal_generators as sg
import config

current_frame = 0

class Player:
    def __init__(self, eventStart, eventFinished):
        self.eventStart = eventStart
        self.eventFinished = eventFinished
        self.data = []

    def _callback(self, outdata, frames, time, status):
        global current_frame
        if status:
            print(status)
        chunksize = min(len(self.data) - current_frame, frames)

        tmp = self.data[current_frame:current_frame + chunksize]
        # stereo -> mono
        if tmp.shape[1] == 2:
            tmp = np.array([np.array([(s[0] + s[1]) / 2]) for s in tmp])
      
        outdata[:chunksize] = tmp
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        current_frame += chunksize

    def play(self, signal, **kwargs):
        signal = np.transpose(signal)
        self.data = signal[1].reshape(-1, 1)

        stream = sd.OutputStream(device=sd.default.device, channels=1, callback=self._callback,
                            samplerate=config.SAMPLERATE, finished_callback=self.eventFinished.set)

        with stream:
            self.eventStart.set()
            self.eventFinished.wait()
            print("playback finished")

    def playFile(self, filename):
        self.data, fs = sf.read(filename, always_2d=True)

        stream = sd.OutputStream(
            samplerate=fs, device=sd.default.device, channels=1,
            callback=self._callback, finished_callback=self.eventFinished.set)

        with stream:
            self.eventStart.set()
            self.eventFinished.wait()
            print("playback finished")