from picozero import Stepper, pico_led
from time import sleep

# Create devices
stepper = Stepper((1, 2, 3, 4), step_sequence="half", step_delay=0.003)

print("Stepper Motor Positioning Demo")
print("Press Ctrl+C to exit")
print()

# Define preset positions in degrees
positions = [0, 90, 180, 270, 360, 270, 180, 90]  # Forward and return cycle
position_names = [
    "Home",
    "90° CW",
    "180° CW",
    "270° CW",
    "Full rotation",
    "270° CCW",
    "180° CCW",
    "90° CCW",
]






def demonstrate_positioning_methods():
    """Demonstrate different positioning approaches."""
    print("=== POSITIONING METHOD COMPARISON ===")
    print()

    # Method 1: Using turn() for relative positioning
    print("Method 1: Using turn() for relative angle movement")
    stepper.reset_position()
    print("  turn(90, 'cw') - turn 90° clockwise from current position")
    stepper.turn(90, 'cw')
    print(f"  ✓ Position: {stepper.angle:.1f}°")
    
    print("  turn(45, 'ccw') - turn 45° counter-clockwise from current position")
    stepper.turn(45, 'ccw')
    print(f"  ✓ Position: {stepper.angle:.1f}°")
    print()

    sleep(1)

    # Method 2: Using turn_to() for absolute positioning
    print("Method 2: Using turn_to() for absolute angle positioning")
    stepper.reset_position()

    print("  turn_to(120, 'cw') - move to 120° position")
    stepper.turn_to(120, 'cw')
    print(f"  ✓ Position: {stepper.angle:.1f}°")

    print("  turn_to(60, 'cw') - move to 60° position")
    stepper.turn_to(60, 'cw')
    print(f"  ✓ Position: {stepper.angle:.1f}°")
    print()

    sleep(1)


# Start demonstration
stepper.reset_position()
print(f"Starting position: {stepper.angle}° ({stepper.step_count} steps)")
print()

try:
    # Demonstrate positioning methods
    demonstrate_positioning_methods()

    # Main positioning sequence
    print("=== AUTOMATIC POSITIONING SEQUENCE ===")
    print("Moving through preset positions using turn_to()...")
    print()

    for i, (target_pos, name) in enumerate(zip(positions, position_names)):
        print(f"Step {i+1}/8: {name} ({target_pos}°)")
        pico_led.on()
        stepper.turn_to(target_pos, 'cw')
        pico_led.off()
        print(f"  ✓ Position: {stepper.angle:.1f}° ({stepper.step_count} steps)")
        sleep(1.5)

    print("=== ADVANCED POSITIONING DEMO ===")
    print("Demonstrating precise positioning capabilities...")
    print()

    # Reset and demonstrate fractional positioning
    stepper.reset_position()

    # Small precise movements
    precise_positions = [22.5, 67.5, 112.5, 157.5, 202.5]
    for pos in precise_positions:
        print(f"Moving to {pos}°...")
        pico_led.on()
        stepper.turn_to(pos, 'cw')
        pico_led.off()
        print(f"  ✓ Position: {stepper.angle:.1f}° ({stepper.step_count} steps)")
        sleep(1)

    # Return home
    print("Returning to home position (0°)...")
    pico_led.on()
    stepper.turn_to(0, 'cw')
    pico_led.off()
    print(f"  ✓ Position: {stepper.angle:.1f}° ({stepper.step_count} steps)")

    print()
    print("Positioning demonstration complete!")

except KeyboardInterrupt:
    print("\nInterrupted by user")

finally:
    # Clean shutdown
    stepper.off()
    pico_led.off()
    stepper.close()
    pico_led.close()
