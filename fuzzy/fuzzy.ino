// Arduino Fuzzy Motor Control UART Interface
// Receives PWM command from PC
// Reports motor speed (float RPM) to PC

// Pin definitions
const int pwmPin = 9;  // PWM pin to motor driver

// Variables
uint8_t pwmValue = 0;
unsigned long lastSerialTime = 0;
const unsigned long serialInterval = 100;  // 100 ms reporting interval

void setup() {
  Serial.begin(9600);  // Baud rate, must match Python side
  pinMode(pwmPin, OUTPUT);
}

void loop() {
  // Read PWM value from UART if available
  if (Serial.available() > 0) {
    pwmValue = Serial.read();
    analogWrite(pwmPin, pwmValue);
  }

  // Periodically send current motor speed back to PC
  if (millis() - lastSerialTime >= serialInterval) {
    lastSerialTime = millis();

    float currentSpeedRPM = readMotorSpeed();
    
    // Send current speed as float with 2 decimal places
    Serial.println(currentSpeedRPM, 2);
  }
}

// Placeholder function for motor speed reading
float readMotorSpeed() {
  // Replace this with actual encoder reading logic
  // For now, return a dummy float value for testing
  static float fakeRPM = 150.0;
  
  // Optional: vary fake RPM to simulate dynamics
  fakeRPM += (random(-5, 6)) * 0.1;  // random small variation
  if (fakeRPM < 0) fakeRPM = 0;
  return fakeRPM;
}

