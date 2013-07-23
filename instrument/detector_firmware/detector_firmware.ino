#include <SPI.h>
#include <stdio.h>
#include <PID_v1.h>
#define BUFFER_SIZE 2048

const byte READ  =     B00001100;  // Read command
const byte WRITE1 =    B00000000;  // Write command
const byte READ2 =     B00011100;  // Read command
const byte WRITE2 =    B00010000;  // Write command
const byte INCREASE =  B00000100;  // Init opcode command
const byte DECREASE =  B00001000;  // Reset opcode command


// pins used for the connection with the sensor
// the other you need are controlled by the SPI library):
const int TEMP1_PIN = 3;
const int TEMP2_PIN = 2;
const int LED1_PIN = 6;
const int LED2_PIN = 7;
const int CURRENT1_PIN = 3;
const int CURRENT2_PIN = 5;
const int CHIPS_PIN = 4;

const double RW = 2;

//Define Variables we'll be connecting to
double  inputT1, outputT1, setpoint1;
double  inputT2, outputT2, setpoint2;

//Specify the links and initial tuning parameters
//PID tempPID1(&inputT1, &outputT1, &setpoint1, 2, 5, 1, DIRECT);
//PID tempPID2(&inputT2, &outputT2, &setpoint2, 2, 5, 1, DIRECT);


volatile int state = LOW;
bool bufferFlag = false;

void setup() { 
  // Init Serial comunication with PC
  Serial.begin(14400, SERIAL_8N1);
  
  // Init the SPI library
  SPI.begin();
  // Configure SPI transmission
  SPI.setDataMode(SPI_MODE0);
  SPI.setBitOrder(MSBFIRST);
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  //digitalWrite(5, LOW);  
  
  
  // Init and configure PID
  //initialize the variables we're linked to
  inputT1 = analogRead(TEMP1_PIN);
  inputT2 = analogRead(TEMP2_PIN);
  setpoint1 = 300;
  setpoint2 = 30;
  //turn the PID on
  //tempPID1.SetMode(AUTOMATIC);
  //tempPID2.SetMode(AUTOMATIC);
  
  // Configure Leds
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);

  pinMode(CURRENT1_PIN, OUTPUT);  
  pinMode(CURRENT2_PIN, OUTPUT);
  pinMode(CHIPS_PIN, OUTPUT);
}


void setResistance(int res, int rn){
   // Convert to n
   digitalWrite(CHIPS_PIN, LOW);
   byte n = (res - 110) / 20; // 5K Ohm  
   if (rn == 0)
     SPI.transfer(WRITE1);
   else
     SPI.transfer(WRITE2);
   SPI.transfer(res);
   digitalWrite(CHIPS_PIN, HIGH);
}

// Read Status of tunable resistor
void readSPI(int addr = 0){
    byte b_add = addr << 4;
    byte n;
    digitalWrite(CHIPS_PIN, LOW);
    Serial.print(addr);
    Serial.print(" - SPI: ");
    //Serial.print(READ | b_add, BIN);
    //Serial.print(" ");
    n = SPI.transfer(READ | b_add);
    Serial.print(n, HEX);
    n = SPI.transfer(NULL);
    Serial.println(n, HEX);
    digitalWrite(CHIPS_PIN, HIGH);
}

/* Test routine
turn temp on and off
change values of resistors
write the resistor status back
*/
void test() {
  byte n;
  
  // Switch between two configurations
  Serial.println("R  1");
  analogWrite(CURRENT1_PIN, 0);
  analogWrite(CURRENT2_PIN, 0);
  setResistance(0, 0);
  setResistance(3000, 1);
  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, LOW);
  delay(1000);
  
  // Read resistor state and send through serial
  readSPI(0);
  readSPI(1);

  // Switch to the second configuration
  Serial.println("R  2");
  setResistance(255, 0);
  setResistance(1500, 1);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, HIGH);
  delay(1000);
 
  readSPI(0);
  readSPI(1);
}

int out_v = 0;

void testTemp(){
  // Ramp the current and measure the temperatur
  out_v += 5;
  if (out_v > 255){
    out_v = 0;
  }
  analogWrite(CURRENT1_PIN, out_v);
  analogWrite(CURRENT2_PIN, out_v);
  delay(500)
  // Read temperature  
  int t1 = analogRead(TEMP1_PIN);
  int t2 = analogRead(TEMP2_PIN);
  // Print temperature on serial
  Serial.print("T ");
  Serial.print(out_v);
  Serial.print(" ");
  Serial.print(t1);
  Serial.print(" ");
  Serial.print(t2);
  Serial.println("");  
  
  if (t1 > 100) || (t2 > 100){
    // If temperature is too high, abort
    analogWrite(CURRENT1_PIN, 0);
    analogWrite(CURRENT2_PIN, 0);
    out_v = -1;
    for (int i = 0; i <5; i++){ 
      digitalWrite(LED1_PIN, HIGH);
      digitalWrite(LED2_PIN, LOW);
      delay(200)
      digitalWrite(LED1_PIN, LOW);
      digitalWrite(LED2_PIN, HIGH);
      delay(200)
    }
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
  }
  

}

void loop() {
  test();
}

