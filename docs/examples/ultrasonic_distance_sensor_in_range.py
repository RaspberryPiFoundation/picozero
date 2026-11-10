from picozero import DistanceSensor, pico_led, pause

ds = DistanceSensor(echo=2, trigger=3, threshold_distance=0.2)

ds.when_in_range = pico_led.on
ds.when_out_of_range = pico_led.off

pause()
