import numpy as np
from scipy import signal
import threading

def sin(event, t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def sawtooth(event, t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def square(event, t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

def whiteNoise(event, t, amplitude):
    return amplitude * np.random.randn(len(t))

def sineSweep(event, t, amplitude, freqStart, freqEnd, sweepRate):
    f = freqStart * 2**(t * sweepRate)
    if (f > freqEnd).any():
        event.set()
    return sin(event, t, amplitude, f)