import numpy as np
import sounddevice as sd
import soundfile as sf
import signal_generators as sg
import config

current_frame = 0

class Player:
    def __init__(self, eventStartedPlayback, eventFinishedPlayback):
        self.eventStartedPlayback = eventStartedPlayback
        self.eventFinishedPlayback = eventFinishedPlayback
        self.data = []

    def _callback(self, outdata, frames, time, status):
        global current_frame
        if status:
            print(status)
        chunksize = min(len(self.data) - current_frame, frames)

        outdata[:chunksize] = self.data[current_frame:current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        current_frame += chunksize

    def play(self, signal, samplerate, **kwargs):
        signal = np.transpose(signal)
        self.data = signal[1].reshape(-1, 1)

        # self.data = signal

        stream = sd.OutputStream(device=sd.default.device, channels=1, callback=self._callback,
                            samplerate=samplerate, finished_callback=self.eventFinishedPlayback.set)

        with stream:
            self.eventStartedPlayback.set()
            self.eventFinishedPlayback.wait()
            print("playback finished")

    def playFile(self, filename):
        self.data, fs = sf.read(filename, always_2d=True)

        stream = sd.OutputStream(
            samplerate=fs, device=sd.default.device, channels=1,
            callback=self._callback, finished_callback=self.eventFinishedPlayback.set)

        with stream:
            self.eventStartedPlayback.set()
            self.eventFinishedPlayback.wait()
            print("playback finished")