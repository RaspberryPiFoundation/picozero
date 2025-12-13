# Contributing Examples

This guide helps contributors create consistent, pedagogical examples for picozero.

## Example Types

### 1. Demo Files (`[component]_demo.py`)

**Purpose:** Concise API reference. Shows core features and common patterns.

**Scope:**
- Core properties and methods only (e.g., `LED.on()`, `LED.brightness`, `RGBLED.color`)
- Basic animations with bounded loops (no `while True` unless clearly bounded)
- Single component focus
- ~15–25 lines of code

**Structure:**
```python
"""
Demonstrates core features of [Component].

Required hardware:
- Raspberry Pi Pico
- [Component] connected to GPIO pins X, Y, Z (see wiring below)
- [Any additional components]

Wiring:
[Simple ASCII diagram or clear pin mapping]
"""

from picozero import [Component]
from time import sleep

component = [Component](...)

# Core feature 1
component.feature1 = value
sleep(0.5)

# Core feature 2
component.feature2 = value
sleep(0.5)
```

**Guidelines:**
- Clear comments for each feature block
- Consistent pin numbering (refer to standard Pico pinout)
- Include wiring diagram or pin description
- Avoid complex logic or state management
- No dependencies beyond picozero and stdlib (time, random, etc.)

### 2. Project Examples (`[component]_[project].py`)

**Purpose:** Real-world, engaging projects. Show practical use of the component in context.

**Scope:**
- Single component focus (what the component *does* in a realistic scenario)
- State management, timing, or interactive logic
- Practical use case (e.g., analog clock with stepper, automatic blinds, robot motion)
- Onboard LED is acceptable for simple feedback/status indication
- ~40–80 lines of code

**Note:** For complex multi-component projects, link users to the [Raspberry Pi Foundation projects site](https://projects.raspberrypi.org/) instead.

**Structure:**
```python
"""
[Project Name]: [One-line description]

A practical example demonstrating [what this teaches].

Required hardware:
- Raspberry Pi Pico
- [List components with quantities]

Optional hardware:
- [Enhancement parts]

Wiring:
[ASCII diagram or detailed pin mapping]

How it works:
[2–3 sentence overview of the logic]
"""

from picozero import [Component1, Component2]
from time import sleep

# Configuration
[CONSTANTS, pin definitions, thresholds]

# Setup
[Initialize components]

try:
    # Main loop or logic
    [Implementation]
finally:
    # Cleanup
    [component.off() for component in [...]]
```

**Guidelines:**
- Include `try/finally` to ensure cleanup (LEDs off, motors stopped)
- Document state/timing logic with comments
- Group related setup; keep logic readable
- Use descriptive variable names
- Mention alternatives or extensions in comments (e.g., "For continuous operation, replace `sleep(1)` with a loop")
- Test on actual hardware before submitting

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Demo | `[component]_demo.py` | `led_demo.py`, `servo_demo.py` |
| Project | `[component]_[project].py` | `servo_drawbot.py`, `rgb_mood_light.py` |
| Existing simple | Keep as-is (migration optional) | `led_blink.py`, `button_function.py` |

## Best Practices

### Wiring
- Use clear ASCII diagrams for simple setups
- Reference official Pico pinout (use pin numbers, not names)
- Example:
  ```
  Pico GPIO  Component
  ─────────  ─────────
  GP2        LED (anode)
  GND        LED (cathode via 330Ω resistor)
  ```

### Pin Choices
- **Demos:** Use low GPIO numbers (1–8) for simplicity
- **Projects:** Use higher numbers (10+) to avoid conflicts
- Always comment pin assignments and allow easy substitution
- Avoid hardcoding pin names; make substitution obvious

### Code Style
- Follow [PEP 8](https://pep8.org/) (4-space indentation)
- Use `from time import sleep` for delays
- Avoid heavy CPU use (tight loops without `sleep`)
- Keep loops bounded or clearly controllable (e.g., `for i in range(10):` not `while True:` unless documented)

### Comments & Docstrings
- One-line description at top (component name + goal)
- Hardware section: what you need to run it
- Wiring section: how to connect it
- Inline comments: explain non-obvious logic, feature grouping
- Example:
  ```python
  # Gradually brighten
  for brightness in range(0, 256, 5):
      led.brightness = brightness / 255
      sleep(0.05)
  ```

### Testing
- Test on actual Pico hardware if possible
- Verify imports and dependencies work
- Ensure cleanup (LEDs off, motors stopped) on exit
- Check for MicroPython compatibility (avoid Python 3.9+ features)

## Pull Request Checklist

- [ ] Example file follows naming convention
- [ ] Docstring includes hardware, wiring, and purpose
- [ ] Code is tested on hardware (or hardware-agnostic design noted)
- [ ] Comments explain feature groups and non-obvious logic
- [ ] No imports beyond picozero and stdlib
- [ ] Cleanup (try/finally) included for demos with loops
- [ ] Wiring diagram or pin mapping provided
- [ ] Example is self-contained and runnable as-is

## Questions?

Refer to existing examples in this directory or open an issue on the [picozero repository](https://github.com/RaspberryPiFoundation/picozero/issues).
