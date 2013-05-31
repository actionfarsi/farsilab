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
const int TEMP1_PIN = 3;
const int TEMP2_PIN = 2;
const int LED1_PIN = 6;
const int LED2_PIN = 7;
const int CURRENT1_PIN = 2;
const int CURRENT2_PIN = 3;
const int COMMMAND_PIN = 4;

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
  Serial.begin(9800);
  
  // Init the SPI library
  SPI.begin();
  // Configure SPI transmission
  SPI.setDataMode(SPI_MODE0);
  SPI.setBitOrder(MSBFIRST);
  digitalWrite(5, LOW);  
  
  
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
  pinMode(CURRENT1_PIN, OUTPUT);
}



void setResistance(int res, int rn){
   // Convert to n
   byte n = (res - 110) / 20; // 5K Ohm  
   if (rn == 0)
     SPI.transfer(WRITE1);
   else
     SPI.transfer(WRITE2);
   SPI.transfer(res);
}



void loop() {
  //Serial.print('R1');
  //analogWrite(CURRENT1_PIN, 254);
  //analogWrite(CURRENT2_PIN, 0);
  setResistance(150, 0);
  setResistance(3000, 1);
  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, LOW);
  delay(3000);
  //Serial.print('R2');
  setResistance(300, 0);
  setResistance(1500, 1);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, HIGH);
  delay(3000);
  
  if (Serial.available()){
    SPI.transfer(READ1);
    byte n = SPI.transfer(NULL);
    Serial.print(n);
  }
}
