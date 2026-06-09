from scipy import signal
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt
import config

NPERSEG = 1024

def fft(t, u, samplerate=config.configData["audioSamplerate"]):
    xf = np.fft.fftfreq(np.array(t).shape[-1], d=1/samplerate)
    yf = np.fft.fft(u)

    plt.plot(xf, yf.real)
    plt.grid()
    plt.show()

    return xf, yf

def invfft(F):
    return np.fft.ifft(F).real

def psd(y): TODO: use returned samplerate
    f, pxx = signal.welch(y, config.configData["audioSamplerate"], nperseg=NPERSEG)
    # plt.semilogy(f, pxx)
    # plt.xlabel('frequency [Hz]')
    # plt.ylabel('PSD [V**2/Hz]')
    # plt.ylim([0.5e-12, 1])
    # plt.grid()
    # plt.show()

    return np.transpose(np.array([f, pxx]))

def lpf(u, cutoff, order=config.configData["audioFilterOrder"]):
    b, a = signal.butter(order, cutoff, fs=config.configData["audioSamplerate"], btype='low', analog=False)
    return signal.lfilter(b, a, u)

def hpf(u, cutoff, order=config.configData["audioFilterOrder"]):
    b, a = signal.butter(order, cutoff, fs=config.configData["audioSamplerate"], btype='high', analog=False)
    return signal.lfilter(b, a, u)