import player
import signal_generators as sg

FREQ = 440
AMPLITUDE = .01

player.play(sg.whiteNoise, AMPLITUDE)