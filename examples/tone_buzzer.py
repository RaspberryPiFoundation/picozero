from time import sleep
from picozero import Speaker

speaker = Speaker(10)

speaker.play()

sleep(1)

def tada():
    c_note = 523
    speaker.play(c_note, 0.1)
    sleep(0.1)
    speaker.play(c_note, 0.4)
    for i in range(100, 0, -1):
        speaker.play(c_note, 0.01, i/100)

tada()
sleep(1)

def chirp():
    global speaker
    for _ in range(5):
        for i in range(5000, 2999, -100):
          speaker.play(i, 0.01)
        sleep(0.2)

chirp()

speaker.off()
