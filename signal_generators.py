import numpy as np
from scipy import signal
import scipy as sc
import matplotlib.pyplot as plt
import soundfile as sf
import config
import filters

PLOT_SIGNAL = False
convertToDisp = True # this flag is set when a signal generator is called

g = 9.81

def decoratorSg(f):
    def decorated(*args, **kwargs):
        print("generating signal...")
        t, y, samplerate = f(*args, **kwargs)
        print("acc rms:", calcRMS(y))
        print("acc max amplitude:", max(y))

        ret = {
            "samplerate": samplerate,
            "uAcc": np.transpose(np.array([t, y]))
        }

        if PLOT_SIGNAL:
            filters.psd(y)
            # plt.plot(t, y)

        if convertToDisp:
            y = accToDisp(t, y) # convert to disp
            
            if PLOT_SIGNAL:
                # plt.plot(t, y)
                # plt.grid()
                # plt.show()
                filters.psd(y)

            print("disp rms:", calcRMS(y))
            print("disp max amplitude:", max(y))

        ret.setdefault("uDisp", np.transpose(np.array([t, y])))
        return ret

    return decorated

def calcRMS(y):
    return np.sqrt(np.sum(y**2) / len(y))

def integrate(t, y):
    dt = t[1] - t[0]

    I = 0
    ret = [0]
    for i in range(1, len(y)):
        I += dt * y[i]
        ret.append(I)

    # remove dc offset
    dc = np.mean(ret)
    ret -= dc

    return t, ret

### do we even need this??? ###
def accToDisp(t, y):
    _, x = integrate(*integrate(t, y))
    x = filters.hpf(x, config.configData["audioDispCutoffFreq"])
    return x

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
        t.append(tStart)
        y.append(_sin(tStart, amplitudeg, f))
        tStart += 1/config.configData["audioSamplerate"]
    
    t = np.array(t)
    y = np.array(y)

    return t, y, config.configData["audioSamplerate"]

# # generate sin signal
# @decoratorSg
# def sin(lengths, amplitudeg, freq):
#     t = _gent(lengths)
#     ret = np.array([t, _sin(t, calcAmp(freq, amplitudeg), freq)])
#     return np.transpose(ret)

# # generate sawtooth signal
# @decoratorSg
# def sawtooth(lengths, amplitudeg, freq):
#     t = _gent(lengths)
#     ret = np.array([t, _sawtooth(t, amplitudeg, freq)])
#     return np.transpose(ret)

# # generate square signal
# @decoratorSg
# def square(lengths, amplitudeg, freq):
#     t = _gent(lengths)
#     ret = np.array([t, _square(t, amplitudeg, freq)])
#     return np.transpose(ret)

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

    return t, y, config.configData["audioSamplerate"]

@decoratorSg
def audioFile(filename):
    signal, samplerate = sf.read("../data/audioFiles/" + filename, always_2d=True)
    signal = np.array([[i/samplerate, (signal[i][0] + signal[i][1]) / 2] for i in range(len(signal))])
    signal = np.transpose(signal)
    return signal[0], signal[1], samplerate