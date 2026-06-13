from scipy import signal
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt
import config

NPERSEG = 1024 * 8

def fft(t, u):
    xf = np.fft.fftfreq(np.array(t).shape[-1], d=t[1]-t[0])
    yf = np.fft.fft(u)

    plt.plot(xf, yf.real)
    plt.grid()
    plt.show()

    return xf, yf

def invfft(F):
    return np.fft.ifft(F).real

def psd(y, samplerate):
    f, pxx = signal.welch(y, samplerate, nperseg=NPERSEG)
    return np.transpose(np.array([f, pxx]))

def lpf(u, cutoff, order=config.configData["audioFilterOrder"]):
    b, a = signal.butter(order, cutoff, fs=config.configData["audioSamplerate"], btype='low', analog=False)
    return signal.lfilter(b, a, u)

def hpf(u, cutoff, order=config.configData["audioFilterOrder"]):
    b, a = signal.butter(order, cutoff, fs=config.configData["audioSamplerate"], btype='high', analog=False)
    return signal.lfilter(b, a, u)