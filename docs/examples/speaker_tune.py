from picozero import Speaker

speaker = Speaker(5)

tetris = [ ['e4', 1], ['b3', 0.5], ['c4', 0.5], ['d4', 1], ['c4', 0.5], ['b3', 0.5],  ['a3', 1], ['a3', 0.5], ['c4', 0.5], ['e4', 1], ['d4', 0.5], ['c4', 0.5],
           ['b3', 1.5], ['c4', 0.5], ['d4', 1], ['e4', 1], ['c4', 1], ['a3', 1], ['a3', 2]]

try:
    speaker.play(tetris)
       
finally: # Turn speaker off if interrupted
    speaker.off()
