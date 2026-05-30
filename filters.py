from scipy import signal
import scipy as sc
import numpy as np
import matplotlib.pyplot as plt
import config

def fft(t, u):
    N = len(t)
    dw = 10 / (2*N) # ???

    yf = sc.fft.fft(u)
    yf = sc.fft.fftshift(yf)
    xf = sc.fft.fftfreq(N, dw)
    xf = sc.fft.fftshift(xf)
    plt.plot(xf, 1.0/N * np.abs(yf))
    plt.grid()
    plt.show()

    return xf, yf

def invfft(F):
    F = sc.fft.fftshift(F)
    return sc.fft.ifft(F).real

def psd(y):
    f, pxx = signal.welch(y, config.configData["audioSamplerate"], nperseg=1024)
    plt.semilogy(f, pxx)
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    # plt.ylim([0.5e-12, 1])
    plt.grid()
    plt.show()

    return f, pxx

def lpf(u, cutoff, order=config.configData["filterOrder"]):
    b, a = signal.butter(order, cutoff, fs=config.configData["audioSamplerate"], btype='low', analog=False)
    return signal.lfilter(b, a, u)

def hpf(u, cutoff, order=config.configData["filterOrder"]):
    b, a = signal.butter(order, cutoff, fs=config.configData["audioSamplerate"], btype='high', analog=False)
    return signal.lfilter(b, a, u)