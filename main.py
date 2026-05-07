import threading
import time
import player
import signal_generators as sg

FREQ = 440
AMPLITUDE = .01

def targetPlayer(p, generator, **kwargs):
    p.play(generator, **kwargs)

def targetAnalyzer(p):
    # wait for player to start playing
    while(p.playing == False): pass

    while(p.playing):
        print(p.t)
        time.sleep(0.1)

p = player.Player()
playerThread = threading.Thread(target=targetPlayer, args=(p, sg.sineSweep,),
                                kwargs={"amplitude": AMPLITUDE, "freqStart": 100, "freqEnd": 1000, "sweepRate": 1/2})
analyzerThread = threading.Thread(target=targetAnalyzer, args=(p,))

playerThread.start()
analyzerThread.start()

playerThread.join()
analyzerThread.join()

# player.playFile("files/Barbie Girl - Aqua.wav", 0.7)