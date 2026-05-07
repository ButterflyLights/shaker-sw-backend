import numpy as np
from scipy import signal
import config

def _gent(length):
    return np.arange(length*config.SAMPLERATE) / config.SAMPLERATE

def _sin(t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def _sawtooth(t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def _square(t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

def _whiteNoise(t, amplitude):
    return amplitude * np.random.randn(len(t))

def sineSweepFreq(t, freqStart, freqEnd, sweepRate):
    return freqStart * 2**(t * sweepRate)

def sineSweep(amplitude, freqStart, freqEnd, sweepRate):
    t = 0
    f = freqStart
    ret = []
    while (f < freqEnd):
        f = sineSweepFreq(t, freqStart, freqEnd, sweepRate)
        ret.append([t, _sin(t, amplitude, f)])
        t += 1/config.SAMPLERATE

    return np.array(ret)

def sin(length, amplitude, freq):
    t = _gent(length)
    ret = ([t, _sin(t, amplitude, freq)])
    return np.transpose(ret)

def sawtooth(length, amplitude, freq):
    t = _gent(length)
    ret = ([t, _sawtooth(t, amplitude, freq)])
    return np.transpose(ret)

def square(length, amplitude, freq):
    t = _gent(length)
    ret = ([t, _square(t, amplitude, freq)])
    return np.transpose(ret)

def whiteNoise(length, amplitude):
    t = _gent(length)
    ret = ([t, _whiteNoise(t, amplitude)])
    return np.transpose(ret)