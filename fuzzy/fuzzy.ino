#define ngat0 0  // Interrupt pin number (0 = digital pin 2)

volatile int pulse1 = 0;
volatile float wheelRps1 = 0;
volatile float wheelRpm1 = 0;  // New: RPM variable
volatile bool CO_U = false;

// Interrupt Service Routine for encoder pulses
void cntPuls1() {
  pulse1++;
}

// Timer interrupt every 10 ms
ISR(TIMER1_OVF_vect) {
  TCNT1 = 63036;
  CO_U = true;
}

// Timer setup function (for 10ms interrupt with 16 MHz and prescaler 64)
void timer1Init() {
  TCCR1A = 0;
  TCCR1B = 0;
  TIMSK1 = 0;

  TCCR1B |= (1 << CS11) | (1 << CS10);  // Prescaler = 64
  TCNT1 = 40536;                        // Initial value for 10ms overflow
  TIMSK1 = (1 << TOIE1);                // Enable overflow interrupt
}

void setup() {
  Serial.begin(9600);
  attachInterrupt(ngat0, cntPuls1, RISING);  // Use INT0 → pin 2

  cli();        // Disable global interrupts during setup
  timer1Init();
  sei();        // Enable global interrupts
}

void loop() {
  if (CO_U == true) {
    CO_U = false;

    // Compute RPS: pulses / pulses_per_revolution / dt
    wheelRps1 = (pulse1 / 50.0) / 0.01;  // 50 pulses per revolution, dt = 10ms
    wheelRpm1 = wheelRps1 * 60.0;        // Convert to RPM
    pulse1 = 0;

    // Print RPM
    Serial.print("wheelRpm1: ");
    Serial.println(wheelRpm1, 2);  // Print with 2 decimal places
  }
}
