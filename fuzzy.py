import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# Triangle membership function
def triangle(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif x < b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)
# Trap membership function
def trapezoid(x, a, b, c, d):
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif c < x < d:
        return (d - x) / (d - c)


# Membership function parameters
LOW_PARAMS_TRAP  = (-999, -200, -150, 0)
MID_PARAMS_TRI   = (-150, 0, 150)
HIGH_PARAMS_TRAP = (0, 150, 200, 999)

# Output PWM values
PWM_LOW = 50
PWM_MID = 100
PWM_HIGH = 180

# Fuzzy controller
def fuzzy_controller(error):
    mu_low = trapezoid(error, *LOW_PARAMS_TRAP)
    mu_mid = triangle(error, *MID_PARAMS_TRI)
    mu_high = trapezoid(error, *HIGH_PARAMS_TRAP)

    print(f"mu_low: {mu_low:.2f}, mu_mid: {mu_mid:.2f}, mu_high: {mu_high:.2f}")  # Optional debug

    numerator = (mu_low * PWM_LOW) + (mu_mid * PWM_MID) + (mu_high * PWM_HIGH)
    denominator = mu_low + mu_mid + mu_high

    pwm_output = numerator / denominator if denominator != 0 else 0
    pwm_output = max(0, min(255, int(pwm_output)))
    return pwm_output


# Serial setup
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust port if needed
time.sleep(2)

# Desired RPM
desired_speed = 40

# Plot setup
window_size = 100
speed_data = deque([0.0]*window_size, maxlen=window_size)
desired_data = deque([desired_speed]*window_size, maxlen=window_size)
time_data = deque(np.linspace(-window_size, 0, window_size), maxlen=window_size)

plt.ion()
fig, ax = plt.subplots()
line1, = ax.plot(time_data, speed_data, label='Measured Speed (RPM)')
line2, = ax.plot(time_data, desired_data, label='Desired Speed (RPM)', linestyle='--')
ax.set_xlabel('Time (samples)')
ax.set_ylabel('Speed (RPM)')
ax.legend()
ax.grid(True)

# Main loop (without try-except)
try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line != '':
            current_speed = float(line)

            print(f"Current speed: {current_speed:.2f} RPM")

            error = desired_speed - current_speed
            print(f"Error: {error:.2f} RPM")

            pwm_value = fuzzy_controller(error)
            print(f"Sending PWM: {pwm_value}")

            ser.write(bytes([pwm_value]))

            # Update plot data
            speed_data.append(current_speed)
            desired_data.append(desired_speed)
            time_data.append(time_data[-1] + 1)

            line1.set_ydata(speed_data)
            line2.set_ydata(desired_data)
            line1.set_xdata(time_data)
            line2.set_xdata(time_data)
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.01)

        time.sleep(0.1)


except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Stopping motor...")
    ser.write(bytes([0]))  # Send PWM = 0
    time.sleep(0.2)        # Give Arduino time to respond
    ser.close()
    plt.ioff()
    plt.show()
    print("Program terminated.")