import numpy as np
from scipy import signal
import scipy as sc
import matplotlib.pyplot as plt
import config
import filters

# TODO: fix amplitudegs

def decoratorSg(f):
    def decorated(*args, **kwargs):
        print("generating signal...")
        ret = f(*args, **kwargs)
        # filters.fft(np.transpose(ret)[0], np.transpose(ret)[1])
        return ret

    return decorated

def _gent(lengths):
    return np.arange(lengths*config.configData["audioSamplerate"]) / config.configData["audioSamplerate"]

def _sin(t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def _sawtooth(t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def _square(t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

# calculate sweep frequency at t
def sineSweepFreq(t, startFreqHz, endFreqHz, sweepRate):
    if startFreqHz < 1: startFreqHz = 1
    return startFreqHz * 2**(t * sweepRate)

# calculate amplitude at frequency f
def calcAmp(f, amplitudeg):
    amplitude = amplitudeg * 9.81
    return amplitude / (2 * np.pi * f)**2

# generate sweep signal
@decoratorSg
def sineSweep(amplitudeg, startFreqHz, endFreqHz, sweepRateOctMin):
    sweepRate = sweepRateOctMin / 60
    t = 0
    f = startFreqHz
    ret = []
    while (f < endFreqHz):
        print(calcAmp(f, amplitudeg))
        f = sineSweepFreq(t, startFreqHz, endFreqHz, sweepRate)
        ret.append([t, _sin(t, calcAmp(f, amplitudeg), f)])
        t += 1/config.configData["audioSamplerate"]

    return np.array(ret)

# generate sin signal
@decoratorSg
def sin(lengths, amplitudeg, freq):
    t = _gent(lengths)
    ret = np.array([t, _sin(t, amplitudeg, freq)])
    return np.transpose(ret)

# generate sawtooth signal
@decoratorSg
def sawtooth(lengths, amplitudeg, freq):
    t = _gent(lengths)
    ret = np.array([t, _sawtooth(t, amplitudeg, freq)])
    return np.transpose(ret)

# generate square signal
@decoratorSg
def square(lengths, amplitudeg, freq):
    t = _gent(lengths)
    ret = np.array([t, _square(t, amplitudeg, freq)])
    return np.transpose(ret)

# generate white noise signal with max / min frequencies
@decoratorSg
def whiteNoise(lengths, amplitudeg, startFreqHz=None, endFreqHz=None):
    t = _gent(lengths)
    N = len(t)
    dw = 10 / (2*N) # ???

    if startFreqHz == None:
        startFreqHz = 0
    if endFreqHz == None:
        endFreqHz = config.configData["audioSamplerate"] / 2

    xf = sc.fft.fftfreq(N, dw)
    xf = sc.fft.fftshift(xf)

    yf = np.zeros(N)
    for i in range(N):
        if np.abs(xf[i]) > startFreqHz and np.abs(xf[i]) < endFreqHz:
            yf[i] = 1
    yf = yf * np.exp(1j * 2 * np.pi * np.random.rand(N))
    
    y = filters.invfft(yf)
    y = y*amplitudeg/max(y)/config.configData["audioGlobalAmplitudeMultiplier"] # TODO: calculate amplitude based on acceleration

    ret = np.array([t, y])
    return np.transpose(ret)