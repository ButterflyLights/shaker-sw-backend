import numpy as np
from scipy import signal

def sin(t, amplitude, freq, phase=0):
    return amplitude * np.sin(2 * np.pi * freq * t + phase)

def sawtooth(t, amplitude, freq, phase=0):
    return amplitude * signal.sawtooth(2 * np.pi * freq * t + phase)

def square(t, amplitude, freq, phase=0):
    return amplitude * signal.square(2 * np.pi * freq * t + phase)

def whiteNoise(t, amplitude, freq, phase=0):
    return amplitude * np.random.randn(len(t))