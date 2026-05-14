import numpy as np
from scipy import signal
import scipy as sc
import matplotlib.pyplot as plt
import config
import filters

def _gent(length):
    return np.arange(length*config.configData["audioSamplerate"]) / config.configData["audioSamplerate"]

def _sin(t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def _sawtooth(t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def _square(t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

# calculate sweep frequency at t
def sineSweepFreq(t, freqStart, freqEnd, sweepRate):
    return freqStart * 2**(t * sweepRate)

# generate sweep signal
def sineSweep(amplitude, freqStart, freqEnd, sweepRate):
    t = 0
    f = freqStart
    ret = []
    while (f < freqEnd):
        f = sineSweepFreq(t, freqStart, freqEnd, sweepRate)
        ret.append([t, _sin(t, amplitude, f)])
        t += 1/config.configData["audioSamplerate"]

    return np.array(ret)

# generate sin signal
def sin(length, amplitude, freq):
    t = _gent(length)
    ret = np.array([t, _sin(t, amplitude, freq)])
    filters.fft(t, ret[1])
    print(ret[1])
    return np.transpose(ret)

# generate sawtooth signal
def sawtooth(length, amplitude, freq):
    t = _gent(length)
    ret = np.array([t, _sawtooth(t, amplitude, freq)])
    filters.fft(t, ret[1])
    return np.transpose(ret)

# generate square signal
def square(length, amplitude, freq):
    t = _gent(length)
    ret = np.array([t, _square(t, amplitude, freq)])
    filters.fft(t, ret[1])
    return np.transpose(ret)

# generate white noise signal with max / min frequencies
def whiteNoise(length, amplitude, startFreq=None, endFreq=None):
    t = _gent(length)
    N = len(t)
    dw = 10 / (2*N) # ???

    if startFreq == None:
        startFreq = 0
    if endFreq == None:
        endFreq = config.configData["audioSamplerate"] / 2

    xf = sc.fft.fftfreq(N, dw)
    xf = sc.fft.fftshift(xf)

    yf = np.zeros(N)
    for i in range(N):
        if np.abs(xf[i]) > startFreq and np.abs(xf[i]) < endFreq:
            yf[i] = 1
    yf = yf * np.exp(1j * 2 * np.pi * np.random.rand(N))
    
    y = filters.invfft(yf)
    y = y*amplitude/max(y) # TODO: calculate amplitude based on acceleration

    filters.fft(t, y)

    ret = np.array([t, y])
    return np.transpose(ret)