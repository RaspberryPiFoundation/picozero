from picozero import Stepper
from time import sleep

stepper = Stepper((1, 2, 3, 4))

print(f"Starting position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("Using step() with default clockwise direction:")
stepper.step(10)
print(f"Position after step(10): {stepper.step_count} steps")
sleep(0.5)
print()

print("step_clockwise(20):")
stepper.step_clockwise(20)
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step_counterclockwise(15):")
stepper.step_counterclockwise(15)
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step_ccw(5) - short alias:")
stepper.step_ccw(5)
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step(10, direction=1) - numeric:")
stepper.step(10, direction=1)
print(f"Position: {stepper.step_count} steps")
print()

print("step(10, direction='cw') - string abbreviation:")
stepper.step(10, direction='cw')
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step(10, direction='clockwise') - full string:")
stepper.step(10, direction='clockwise')
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("rotate_clockwise(90) - 90 degrees CW:")
stepper.rotate_clockwise(90)
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("rotate(45, direction='ccw') - 45 degrees CCW:")
stepper.rotate(45, direction='ccw')
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("revolve_clockwise() - 1 full revolution CW:")
stepper.revolve_clockwise()  # Default is 1 revolution
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("revolve(0.5, direction=-1) - half revolution CCW:")
stepper.revolve(0.5, direction=-1)
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("Resetting position to home (0 steps, 0°)...")
stepper.reset_position()
print(f"After reset: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print()
print("Final demonstration - all methods achieve the same result:")
for i, (method_name, method_call) in enumerate([
    ("Default direction", lambda: stepper.step(5)),
    ("Numeric direction", lambda: stepper.step(5, direction=1)),
    ("String direction", lambda: stepper.step(5, direction='cw')),
    ("Convenience method", lambda: stepper.step_clockwise(5))
], 1):
    print(f"{i}. {method_name}: 5 steps clockwise")
    method_call()
    
print(f"All methods reached: {stepper.step_count} steps total")

# Turn off motor when done
stepper.off()
stepper.close()
