from picozero import Speaker
from time import sleep

speaker = Speaker(5)
    
BEAT = 0.25 # 240 BPM

dance = [[55, BEAT], ['', BEAT / 2], [55, BEAT], ['', BEAT / 2], [55, BEAT * 1.25], [55, BEAT], ['', BEAT / 2], [55, BEAT],
         [57, BEAT], ['', BEAT / 2], [57, BEAT], ['', BEAT / 2], [54, BEAT * 1.25], [54, BEAT], ['', BEAT / 2], [55, BEAT],
         [55, BEAT], [79, BEAT / 2], [55, BEAT], [79, BEAT / 2], [55, BEAT * 1.25], [55, BEAT], ['', BEAT / 2], [55, BEAT],
         [57, BEAT], [75, BEAT / 2], [57, BEAT], [75, BEAT / 2], [72, BEAT * 1.25], [56, BEAT], ['', BEAT / 2], [56, BEAT]]

try:
    speaker.play(dance)
       
finally: # Turn speaker off if interrupted
    speaker.off()
