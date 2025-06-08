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

# Membership function parameters (adjust here!)
LOW_PARAMS = (-100, -50, 0)
MID_PARAMS = (-50, 0, 50)
HIGH_PARAMS = (0, 50, 100)

# PWM output values for each rule (adjust here!)
PWM_LOW = 80
PWM_MID = 150
PWM_HIGH = 230

# Fuzzy controller
def fuzzy_controller(error):
    mu_low = triangle(error, *LOW_PARAMS)
    mu_mid = triangle(error, *MID_PARAMS)
    mu_high = triangle(error, *HIGH_PARAMS)
    
    numerator = (mu_low * PWM_LOW) + (mu_mid * PWM_MID) + (mu_high * PWM_HIGH)
    denominator = mu_low + mu_mid + mu_high
    
    if denominator == 0:
        pwm_output = 0
    else:
        pwm_output = numerator / denominator

    pwm_output = max(0, min(255, int(pwm_output)))
    return pwm_output

# Serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Change port as needed
time.sleep(2)

# Desired speed (adjustable!)
desired_speed = 200.0

# Plot settings
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

# Main loop
try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                current_speed = float(line)
                print(f"Current speed: {current_speed:.2f} RPM")

                error = desired_speed - current_speed
                pwm_value = fuzzy_controller(error)
                print(f"Sending PWM: {pwm_value}")

                ser.write(bytes([pwm_value]))

                # Update plot
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

            except ValueError:
                pass

except KeyboardInterrupt:
    print("Stopping...")
    ser.close()
    plt.ioff()
    plt.show()

