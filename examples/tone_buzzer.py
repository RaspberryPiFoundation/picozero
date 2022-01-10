# Make some noise!

from time import sleep
from pico import Speaker

speaker = Speaker(14)

speaker.play()

sleep(1)

speaker.play(500, 0.5)

sleep(1)

def chirp():
    global speaker
    for _ in range(5):
        for i in range(5000, 2999, -100):
          speaker.play(i, 0.01)
        sleep(0.2)

chirp()
