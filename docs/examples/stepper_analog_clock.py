from picozero import Stepper

# Second Hand Clock - Continuous 60s Rotation
# One full revolution every 60 seconds.

STEP_DELAY = 60.0 / 2048  # ≈ 0.029296875 seconds per step (full-step)

stepper = Stepper((1, 2, 3, 4), step_delay=STEP_DELAY)

stepper.run_continuous(direction="cw")
