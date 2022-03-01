# Active Buzzer that plays a note when powered
from time import sleep
from picozero import Buzzer

buzzer = Buzzer(10)

buzzer.on()
sleep(1)
buzzer.off()
sleep(1)

buzzer.beep()
sleep(4)
buzzer.off()


