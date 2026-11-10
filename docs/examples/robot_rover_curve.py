from picozero import Robot
from time import sleep

robot_rover = Robot(left=(14,15), right=(12,13))

# drive forward in an arc to the left
robot_rover.forward(curve_left=0.5)
sleep(2)

# go back along the same arc
robot_rover.reverse()
sleep(2)

robot_rover.stop()
