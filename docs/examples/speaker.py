from picozero import Speaker
from time import sleep

speaker = Speaker(5)

def tada():
    c_note = 523
    speaker.play(c_note, 0.1)
    sleep(0.1)
    speaker.play(c_note, 0.9)

def chirp():
    global speaker
    for _ in range(5):
        for i in range(5000, 2999, -100):
          speaker.play(i, 0.01)
        sleep(0.2)


try: 
    tada()
    sleep(1)
    chirp()
    
finally: # Turn the speaker off if interrupted
    speaker.off()
