from picozero import Stepper, pico_led
from time import sleep

# Create devices
stepper = Stepper((1, 2, 3, 4), step_sequence="half", step_delay=0.003)

print("Stepper Motor Positioning Demo")
print("Press Ctrl+C to exit")
print()

# Define preset positions in degrees
positions = [0, 90, 180, 270, 360, 270, 180, 90]  # Forward and return cycle
position_names = ["Home", "90° CW", "180° CW", "270° CW", "Full rotation", "270° CCW", "180° CCW", "90° CCW"]

def move_to_position(target_angle, description=""):
    """Move stepper to target angle from current position."""
    current_angle = stepper.angle
    angle_diff = target_angle - current_angle
    
    print(f"Target: {description} ({target_angle}°)")
    print(f"  Moving from {current_angle:.1f}° to {target_angle}°")
    pico_led.on()  # Indicate movement
    
    if angle_diff > 0:
        print(f"  → Rotating {angle_diff}° clockwise...")
        stepper.rotate_clockwise(angle_diff)
    elif angle_diff < 0:
        print(f"  → Rotating {-angle_diff}° counter-clockwise...")
        stepper.rotate_counterclockwise(-angle_diff)
    else:
        print("  → Already at target position")
    
    pico_led.off()  # Movement complete
    print(f"  ✓ Position: {stepper.angle:.1f}° ({stepper.step_count} steps)")
    print()

def demonstrate_positioning_methods():
    """Demonstrate different positioning approaches."""
    print("=== POSITIONING METHOD COMPARISON ===")
    print()
    
    # Method 1: Using convenience methods (current approach)
    print("Method 1: Convenience methods (rotate_clockwise/rotate_counterclockwise)")
    stepper.reset_position()
    move_to_position(90, "90° using rotate_clockwise")
    move_to_position(45, "45° using rotate_counterclockwise") 
    
    sleep(1)
    
    # Method 2: Using parameterized methods
    print("Method 2: Parameterized methods (rotate with direction parameter)")
    stepper.reset_position()
    
    print("Target: 120° using rotate(120, direction='cw')")
    stepper.rotate(120, direction='cw')
    print(f"  ✓ Position: {stepper.angle:.1f}°")
    
    print("Target: 60° using rotate(60, direction='ccw')")
    stepper.rotate(60, direction='ccw')
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
    print("Moving through preset positions...")
    print()
    
    for i, (target_pos, name) in enumerate(zip(positions, position_names)):
        print(f"Step {i+1}/8:")
        move_to_position(target_pos, name)
        sleep(1.5)
    
    print("=== ADVANCED POSITIONING DEMO ===")
    print("Demonstrating precise positioning capabilities...")
    print()
    
    # Reset and demonstrate fractional positioning
    stepper.reset_position()
    
    # Small precise movements
    precise_positions = [22.5, 67.5, 112.5, 157.5, 202.5]
    for pos in precise_positions:
        move_to_position(pos, f"Precise positioning to {pos}°")
        sleep(1)
    
    # Return home
    move_to_position(0, "Return to home")
    
    print("Positioning demonstration complete!")
    
except KeyboardInterrupt:
    print("\nInterrupted by user")
    
finally:
    # Clean shutdown
    stepper.off()
    pico_led.off()
    stepper.close()
    pico_led.close()
