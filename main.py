import player
import signal_generators as sg

FREQ = 440
AMPLITUDE = .01

# player.play(sg.sineSweep, amplitude=AMPLITUDE, freqStart=100, freqEnd=1000, sweepRate=1/2)
player.playFile("files/Barbie Girl - Aqua.wav", 0.7)