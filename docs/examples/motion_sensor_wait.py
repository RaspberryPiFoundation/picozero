from picozero import MotionSensor

pir = MotionSensor(2)

while True:
    pir.wait_for_motion()
    print("Motion detected!")
    pir.wait_for_no_motion()
    print("Motion stopped")
