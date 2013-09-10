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

const int N_TEMP = 10;
const float T1_b = 2.2;
const float T2_b = 2.2;

//Define Variables we'll be connecting to
double  inputT1, outputT1, setpoint1;
double  inputT2, outputT2, setpoint2;

double k1[3] = {2,5,1}, k2[3]={2,5,1};

int out_v = 0;

//Specify the links and initial tuning parameters
PID tempPID1(&inputT1, &outputT1, &setpoint1, k1[0], k1[1], k1[2], DIRECT);
PID tempPID2(&inputT2, &outputT2, &setpoint2, k2[0], k2[1], k2[2], DIRECT);


//volatile int state = LOW;
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
  
  analogWrite(CURRENT1_PIN, 0);
  analogWrite(CURRENT2_PIN, 0);
    
  pinMode(CHIPS_PIN, OUTPUT);
}


void setResistance(int res, int r_n){
   // Convert to n
   digitalWrite(CHIPS_PIN, LOW);
   byte n = (res - 110) / 20; // 5K Ohm  
   if (r_n == 1)
     SPI.transfer(WRITE1);
   else if (r_n == 2)
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
void testResistor() {
  byte n;
  
  // Switch between two configurations
  Serial.println("R  1");
  analogWrite(CURRENT1_PIN, 0);
  analogWrite(CURRENT2_PIN, 0);
  setResistance(0, 0);
  setResistance(0, 1);
  digitalWrite(LED1_PIN, HIGH);
  digitalWrite(LED2_PIN, LOW);
  delay(1000);
  
  // Read resistor state and send through serial
  readSPI(0);
  readSPI(1);

  // Switch to the second configuration
  Serial.println("R  2");
  setResistance(255, 0);
  setResistance(255, 1);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, HIGH);
  delay(1000);
 
  readSPI(0);
  readSPI(1);
}



void testTemp(){
  // Ramp the current and measure the temperatur
  out_v += 10;
  if (out_v > 255){
    out_v = 0;
  }
  analogWrite(CURRENT1_PIN, out_v);
  analogWrite(CURRENT2_PIN, out_v);
  delay(2000);
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
  
  if ((t1 > 2000) || (t2 > 2000)){
    // If temperature is too high, abort
    analogWrite(CURRENT1_PIN, 0);
    analogWrite(CURRENT2_PIN, 0);
    out_v = -1;
    for (int i = 0; i <5; i++){ 
      digitalWrite(LED1_PIN, HIGH);
      digitalWrite(LED2_PIN, LOW);
      delay(200);
      digitalWrite(LED1_PIN, LOW);
      digitalWrite(LED2_PIN, HIGH);
      delay(200);
    }
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
  }
}




void apdLoop(){
  // Read and integrate temperature
   float t1 = 0, t2 = 0;
   for (int i = 0; i<N_TEMP; i++){
     t1 += analogRead(TEMP1_PIN);
     t2 += analogRead(TEMP2_PIN);
     delay(100);
   }
   
   // Convert to temperature K and average with the previous
   t1 = 0.7 * (t1/N_TEMP)/T1_b + 0.3 * inputT2;
   t2 = 0.7 * (t2/N_TEMP)/T2_b + 0.3 * inputT1;
   
   // Compute the update and change current
   tempPID1.Compute();
   tempPID2.Compute();
   
   analogWrite(CURRENT1_PIN, outputT1);
   analogWrite(CURRENT2_PIN, outputT2);
}

void apdParametersSet(char param, char* buffer, int pid_i) {
  if (pid_i == 1){
    if (param == 'P')    k1[0] = atof(buffer);
    else if (param == 'I')  k1[1] = atof(buffer);
    else if (param == 'D')  k1[2] = atof(buffer);
  tempPID1.SetTunings( k1[0], k1[1], k1[2]);
  }
  if (pid_i == 2){
    if   (param == 'P')  k2[0] = atof(buffer);
    else if (param == 'I')  k2[1] = atof(buffer);
    else if (param == 'D')  k2[2] = atof(buffer);
  tempPID2.SetTunings( k2[0], k2[1], k2[2]);
  }
   
    
}

// Send full state to serial
void apdComm(){
  // Resistor Status
  
  // Temperature Status
  Serial.print("T1 ");
  Serial.print(inputT1);
  Serial.print("SetT ");
  Serial.print(setpoint1);
  Serial.print("Current ");
  Serial.print(outputT1);
  Serial.print("K1");
  Serial.print(tempPID1.GetKp());
  Serial.print(" ");
  Serial.print(tempPID1.GetKi());
  Serial.print(" ");
  Serial.println(tempPID1.GetKd());
  Serial.print("T2 ");
  Serial.print(inputT2);
  Serial.print("SetT ");
  Serial.print(setpoint2);
  Serial.print("Current ");
  Serial.print(outputT2);
  Serial.print("K2");
  Serial.print(tempPID2.GetKp());
  Serial.print(" ");
  Serial.print(tempPID2.GetKi());
  Serial.print(" ");
  Serial.println(tempPID2.GetKd());
  
}

char command_byte = 0;
char values_buffer[64];
int bytes_read;
char state = 'R'; 

void loop() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    command_byte = Serial.read();
    Serial.readBytes(values_buffer, bytes_read);
    switch (command_byte){
      case '1': // Temperature Test
        state = 'T';
        break;
      case '2': // Resistance Test
        out_v = 0;
        state = 'R';
        break;
      case 'A': // Start ADP
        state = 'A'; 
        break;
      case 'a': // Stop ADP
        state = '0';
        break;
      case 's': // Set Resistance1
        setResistance(atof(values_buffer),1);
        break;
      case 'S': // Set Resistance2
        setResistance(atof(values_buffer),2);
        break;
      case 't': // Set Temp1
        setpoint1 = atof(values_buffer);
        break;
      case 'T': // Set Temp2
        setpoint2 = atof(values_buffer);
        break;
      case 'k': // Set Parameters1
        apdParametersSet(values_buffer[0],values_buffer+1,1);
        break;
      case 'K': // Set Parameters2
        apdParametersSet(values_buffer[0],values_buffer+1,2);
        break;
    }
    Serial.flush();
  }
    // Loop for the state
    switch (state){
      case 'T': testTemp();        
        break;
      case 'R': testResistor();        
        break;
      case 'A':
        apdLoop();  // Update 
        apdComm();   // Communication state
    }
    Serial.flush();
   

}

