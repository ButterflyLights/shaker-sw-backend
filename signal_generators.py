import numpy as np
from scipy import signal
import scipy as sc
import matplotlib.pyplot as plt
import config
import filters

# TODO: fix amplitudegs

g = 9.81

def decoratorSg(f):
    def decorated(*args, **kwargs):
        print("generating signal...")
        t, y = f(*args, **kwargs)
        # filters.fft(np.transpose(ret)[0], np.transpose(ret)[1])
        print("rms:", calcRMS(y))
        print("max amplitude:", max(y))
        filters.psd(y)

        # plt.plot(t, y)
        # plt.show()

        y = accToDisp(t, y) # convert to disp

        return np.transpose(np.array([t, y]))

    return decorated

def calcRMS(y):
    # f, psd = filters.psd(y)

    # df = f[1] - f[0]
    # grms = np.sqrt(np.sum(psd * df))
    
    # print("rms psd:", grms)
    # print("direct rms:", np.sqrt(np.sum(y**2) / len(y)))

    return np.sqrt(np.sum(y**2) / len(y))

def accToDisp(t, y, fmin=1):
    xf, yf = filters.fft(t, y)

    # plt.semilogy(xf, yf)

    # normalize
    valid = abs(xf) >= fmin # mask low frequencies
    # yf[valid] = yf[valid] / (2 * np.pi * xf[valid])**2

    for i in range(len(yf)):
        if valid[i]:
            yf[i] = yf[i] / (2 * np.pi * xf[i])**2

    # plt.semilogy(xf, yf)
    # plt.xlim(-1000, 1000)
    # plt.show()

    return filters.invfft(yf)

def _gent(lengths):
    return np.arange(lengths*config.configData["audioSamplerate"]) / config.configData["audioSamplerate"]

def _sin(t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def _sawtooth(t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def _square(t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

# calculate sweep frequency at t
def sineSweepFreq(t, startFreqHz, endFreqHz, sweepRate, fmin=1):
    if startFreqHz < fmin: startFreqHz = fmin
    return startFreqHz * 2**(t * sweepRate)

# calculate amplitude at frequency f
def calcAmp(f, amplitudeg):
    amplitude = amplitudeg * g
    return amplitude / (2 * np.pi * f)**2

# generate sweep signal
@decoratorSg
def sineSweep(amplitudeg, startFreqHz, endFreqHz, sweepRateOctMin):
    sweepRate = sweepRateOctMin / 60
    f = startFreqHz
    tStart = 0
    t = []
    y = []
    while (f < endFreqHz):
        f = sineSweepFreq(tStart, startFreqHz, endFreqHz, sweepRate)
        # ret.append([tStart, _sin(t, amplitudeg, f)])
        t.append(tStart)
        y.append(_sin(tStart, amplitudeg, f))
        tStart += 1/config.configData["audioSamplerate"]

    # calculated amplitude:
    # rms: 5.662339944180496e-07
    # max amplitude: 1.5525061663804428e-06
    
    return t, y

# generate sin signal
@decoratorSg
def sin(lengths, amplitudeg, freq):
    t = _gent(lengths)
    ret = np.array([t, _sin(t, calcAmp(freq, amplitudeg), freq)])
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
def whiteNoise(lengths, grms, startFreqHz=None, endFreqHz=None):
    t = _gent(lengths)
    N = len(t)
    dw = 10 / (2*N) # ???

    if startFreqHz == None:
        startFreqHz = 0
    if endFreqHz == None:
        endFreqHz = config.configData["audioSamplerate"] / 2 # use nyquist freq as frequency limit

    xf = sc.fft.fftfreq(N, dw)
    xf = sc.fft.fftshift(xf)

    yf = np.zeros(N)
    for i in range(N):
        if np.abs(xf[i]) > startFreqHz and np.abs(xf[i]) < endFreqHz:
            yf[i] = 1
    yf = yf * np.exp(1j * 2 * np.pi * np.random.rand(N))
    
    y = filters.invfft(yf)
    y = y * (grms * g) / calcRMS(y) # get desired grms

    return t, y