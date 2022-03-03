from picozero import Speaker

speaker = Speaker(5)

BEAT = 0.5 # 120 BPM

tetris = [ ['e4', BEAT], ['b3', BEAT / 2], ['c4', BEAT / 2], ['d4', BEAT], ['c4', BEAT / 2], ['b3', BEAT / 2],  
           ['a3', BEAT], ['a3', BEAT / 2], ['c4', BEAT / 2], ['e4', BEAT ],['d4', BEAT / 2], ['c4', BEAT / 2], 
           ['b3', BEAT * 1.5], ['c4', BEAT / 2], ['d4', BEAT], ['e4', BEAT], ['c4', BEAT], ['a3', BEAT], ['a3', BEAT * 2]]

try:
    speaker.play(tetris)
       
finally: # Turn speaker off if interrupted
    speaker.off()
