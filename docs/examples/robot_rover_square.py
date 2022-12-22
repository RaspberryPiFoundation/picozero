from picozero import Robot

robot_rover = Robot(left=(14,15), right=(12,13))

for i in range(4):
    # move forward for 1 second
    robot_rover.forward(t=1, wait=True)
    # rotate to the left for 1 second
    robot_rover.left(t=1, wait=True)
