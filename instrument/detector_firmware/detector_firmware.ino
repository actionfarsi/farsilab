#include <SPI.h>
#include <stdio.h>
#include <PID_v1.h>
#define BUFFER_SIZE 2048

const byte READ1 =     B00001100;  // Read command
const byte WRITE1 =    B00000000;  // Write command
const byte READ2 =     B00011100;  // Read command
const byte WRITE2 =    B00010000;  // Write command
const byte INCREASE =  B00000100;  // Init opcode command
const byte DECREASE =  B00001000;  // Reset opcode command


// pins used for the connection with the sensor
// the other you need are controlled by the SPI library):
const int TEMP1_PIN = 2;
const int TEMP2_PIN = 48;
const int LED1_PIN = 53;
const int LED2_PIN = 47;
const int CURRENT1_PIN = 14;
const int CURRENT2_PIN = 14;

//Define Variables we'll be connecting to
double  inputT1, outputT1, setpoint1;
double  inputT2, outputT2, setpoint2;

//Specify the links and initial tuning parameters
PID tempPID1(&inputT1, &outputT1, &setpoint1, 2, 5, 1, DIRECT);
PID tempPID2(&inputT2, &outputT2, &setpoint2, 2, 5, 1, DIRECT);


volatile int state = LOW;
bool bufferFlag = false;

void setup() { 
  // Init Serial comunication with PC
  Serial.begin(9800);
  
  // Init the SPI library
  SPI.begin();
  // Configure SPI transmission
  SPI.setDataMode(1);
  SPI.setBitOrder(MSBFIRST);
  
  // Init and configure PID
  //initialize the variables we're linked to
  inputT1 = analogRead(TEMP1_PIN);
  inputT2 = analogRead(TEMP2_PIN);
  setpoint1 = 300;
  setpoint2 = 30;
  //turn the PID on
  tempPID1.SetMode(AUTOMATIC);
  tempPID2.SetMode(AUTOMATIC);
  
  // Configure Leds
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
}

void setResistance(int res, int rn){
   // Convert to n
   byte n = 256 *(res - RW) / 5000; // 5K Ohm  
   if (rn == 0)
     SPI.transfer(WRITE1);
   else
     SPI.transfer(WRITE2);
   SPI.transfer(n);
}



void loop() {
  Serial.print('R1');
  setResistance(500, 0);
  setResistance(5000, 1);
  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, LOW);
  sleep(10);
  Serial.print('R2');
  setResistance(500, 1);
  setResistance(5000, 0);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, HIGH);
  sleep(10);
  
  if (Serial.available()){
    
    Serial.flush();
  }
}
