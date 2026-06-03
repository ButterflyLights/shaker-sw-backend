import numpy as np
import sounddevice as sd
import soundfile as sf
import signal_generators as sg
import config

class Player:
    def __init__(self, eventStartedPlayback, eventFinishedPlayback):
        self.eventStartedPlayback = eventStartedPlayback
        self.eventFinishedPlayback = eventFinishedPlayback
        self.data = []
        self.current_frame = 0

    def _preprocess(self, signal):
        signal = np.transpose(signal)

        # normalize signal if amplitude is to high
        maxAmp = max(signal[1])
        if maxAmp > config.configData["audioAmplitudeLimit"]:
            signal[1] *= config.configData["audioAmplitudeLimit"] / maxAmp
            print(f"scaled signal to max amplitude of {max(signal[1])}")

        return signal

    def _callback(self, outdata, frames, time, status):
        if status:
            print(status)
        chunksize = min(len(self.data) - self.current_frame, frames)

        outdata[:chunksize] = config.configData["audioGlobalAmplitudeMultiplier"] * self.data[self.current_frame:self.current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        self.current_frame += chunksize

    def play(self, signal, samplerate, **kwargs):
        signal = self._preprocess(signal)

        self.data = signal[1].reshape(-1, 1)

        stream = sd.OutputStream(device=sd.default.device, channels=1, callback=self._callback,
                            samplerate=samplerate, finished_callback=self.eventFinishedPlayback.set)

        with stream:
            print("starting playback")
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