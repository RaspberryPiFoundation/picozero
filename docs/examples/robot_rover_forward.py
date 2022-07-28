from picozero import Robot
from time import sleep

robot_rover = Robot(left=(14,15), right=(12,13))

# move forward
robot_rover.forward()
sleep(1)
robot_rover.stop()
