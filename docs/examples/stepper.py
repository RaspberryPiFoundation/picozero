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

print("step(20, 1) - clockwise:")
stepper.step(20, 1)
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step(15, -1) - counter-clockwise:")
stepper.step(15, -1)
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step(5, 'cw') - short string abbreviation:")
stepper.step(5, "cw")
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step(10, 1) - numeric:")
stepper.step(10, 1)
print(f"Position: {stepper.step_count} steps")
print()

print("step(10, 'cw') - string abbreviation:")
stepper.step(10, "cw")
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

print("step(10, 'clockwise') - full string:")
stepper.step(10, "clockwise")
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()


print("turn(90, 'cw') - 90 degrees CW:")
stepper.turn(90, "cw")
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("turn(45, 'ccw') - 45 degrees CCW:")
stepper.turn(45, "ccw")
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("rotate(1, 'cw') - 1 full rotation CW:")
stepper.rotate(1, "cw")
print(f"Position: {stepper.step_count} steps, {stepper.angle:.1f} degrees")
sleep(0.5)
print()

print("rotate(0.5, 'ccw') - half rotation CCW:")
stepper.rotate(0.5, "ccw")
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
for i, (method_name, method_call) in enumerate(
    [
        ("Default direction", lambda: stepper.step(5)),
        ("Numeric direction", lambda: stepper.step(5, 1)),
        ("String direction", lambda: stepper.step(5, "cw")),
    ],
    1,
):
    print(f"{i}. {method_name}: 5 steps clockwise")
    method_call()

print(f"All methods reached: {stepper.step_count} steps total")

# Advanced methods demonstration
print()
print("=== ADVANCED METHODS ===")
print()

stepper.reset_position()
print("step_to(100, 'cw') - move to absolute step 100 clockwise:")
stepper.step_to(100, "cw")
print(f"Position: {stepper.step_count} steps")
sleep(0.5)
print()

stepper.reset_position()
print("turn_to(180, 'cw') - turn to 180 degrees clockwise:")
stepper.turn_to(180, "cw")
print(f"Position: {stepper.angle:.1f}° ({stepper.step_count} steps)")
sleep(0.5)
print()

print("set_speed(60) - set speed to 60 RPM:")
stepper.set_speed(60)
print(f"Step delay now: {stepper.step_delay:.6f} seconds")
sleep(0.5)
print()

print("step(20, 'cw') - step 20 times at 60 RPM:")
stepper.step(20, "cw")
print(f"Position: {stepper.step_count} steps")
print()

# Turn off motor when done
stepper.off()
stepper.close()
