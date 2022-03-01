from picozero import Speaker
from time import sleep

speaker = Speaker(5, bpm=120)

tetris = [ ['e4', 1], ['b3', 0.5], ['c4', 0.5], ['d4', 1], ['c4', 0.5], ['b3', 0.5],  ['a3', 1], ['a3', 0.5], ['c4', 0.5], ['e4', 1], ['d4', 0.5], ['c4', 0.5],
           ['b3', 1.5], ['c4', 0.5], ['d4', 1], ['e4', 1], ['c4', 1], ['a3', 1], ['a3', 2]]

# Play 'Staccato' half length notes
note_length = 0.5 # play notes for half a beat
gap_length = 1 - note_length # leave half a beat between notes

try:
    for note in tetris:
        speaker.play(note, multiplier=note_length)
        gap = speaker.to_seconds(note[1]) * gap_length # leave a gap between notes
        sleep(gap)
       
finally: # Turn speaker off if interrupted
    speaker.off()
