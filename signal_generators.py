import numpy as np
from scipy import signal
import config

def _sin(t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def _sawtooth(t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def _square(t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

def _whiteNoise(t, amplitude):
    return amplitude * np.random.randn(len(t))

def sineSweep(amplitude, freqStart, freqEnd, sweepRate):
    t = 0
    f = freqStart
    ret = []
    while (f < freqEnd):
        f = freqStart * 2**(t * sweepRate)
        ret.append([t, _sin(t, amplitude, f)])
        t += 1/config.SAMPLERATE

    return np.array(ret)

def sineSweepFreq(t, freqStart, freqEnd, sweepRate):
    return freqStart * 2**(t * sweepRate)