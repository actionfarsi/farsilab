/*
  ReadAnalogVoltage
  Reads an analog input on pin 0, converts it to voltage, and prints the result to the serial monitor.
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.
 
 This example code is in the public domain.
 */
// Arduino
// setPin = A0, directionPin = 8, powerPin=9, tempPin = A1;
const int pins1[4] = {A0,8,9,A1};
const int pins2[4] = {A2,10,11,A3};

// AtTiny
// const int setPin = A0, directionPin = 8, powerPin=9, tempPin = A1;
const float kP = 80.7, kI = 30, kD = 5;
const float dtD = 4, dtI = 20;


float err1[4] = {0,0,0,0};
float err2[4] = {0,0,0,0};

int i = 0;

// the setup routine runs once when you press reset:
void setup() {
   // Direction Pin
   pinMode(pins1[1], OUTPUT);
   pinMode(pins1[2], OUTPUT);
   pinMode(pins2[1], OUTPUT);
   pinMode(pins2[2], OUTPUT);

   Serial.begin(9600); 
}

float readTemp(const int * pins, float setV = 0){
  int N = 10;
  float curTemp = 0;
  float setTemp = 0;
  for (int i = 0; i<N; i++){
    curTemp += analogRead(pins[3]);
    setTemp += analogRead(pins[0]);
    delay(50);
  }
  
  if (setV != 0)
    setTemp = setV*N;
  curTemp = constrainMap(curTemp, 0, 1023*N, 0, 100);  
  setTemp = constrainMap(setTemp, 0, 1023*N, 0, 100);  
  
  //curTemp = 50;
  
  return curTemp-setTemp;
  
}

void pid(float err, float * e){
  // PID
  e[2] = (e[2]* (dtD-1) + (err - e[0]))/dtD; // Error is from previous step
  e[1] = (e[1]* (dtI-1) + e[0])/dtI;
  e[0] =  err;
  
  e[3] = e[0] * kP + e[1] * kI + e[2] *kD;
}

void writeTemp(const int * pins, float * e){
   // Set direction
  if (e[3] > 0){
    digitalWrite(pins[1], HIGH);
  }
  else{
    digitalWrite(pins[1], LOW);
    e[3] = -1 * e[3];
  }
  
  analogWrite(pins[2], constrainMap(e[3], 0, 100, 0, 255));
}

void serialLog(float *e){
  //Serial.print("sensor = " );                       
  //Serial.print(temp1); 
  //Serial.print(" " );    
  //Serial.print(temp2);      
  //Serial.print(" " );
  Serial.print("Error = " );                       
  Serial.print(e[0]);  
  Serial.print("\t output = ");      
  Serial.println(e[3]); 
        
//  Serial.print("\t errorD = ");      
//  Serial.println(errorD);   
}

// the loop routine runs over and over again forever:
void doPID() {
  // Set voltage diode 1 - 439.5 --> 1551.75
  // Set voltage diode 2 - 228.7 --> 1558.5
  
  //pid(readTemp(pins1, 439.5), err1);
  pid(readTemp(pins1, 400.5), err1);
  pid(readTemp(pins2, 500.5), err2);
  //pid(readTemp(pins2, 228.7), err2); 
  
  writeTemp(pins1,err1);
  Serial.print("E1 - P " ); 
  serialLog(err1);  

  writeTemp(pins2,err2);
  Serial.print("E2 - P" ); 
  serialLog(err2);

  
  delay(100);
}

void testBoard(const int * pins){
  int N = 10;
  float curTemp = 0;
  float setTemp = 0;
  for (int i = 0; i<N; i++){
    curTemp += analogRead(pins[3]);
    setTemp += analogRead(pins[0]);
    delay(50);
  }
  Serial.print(curTemp/N);
//  Serial.print('\t');
//  Serial.print(setTemp/N);
  Serial.print('\n');
  delay(500);
}

void testVoltagRamp(const int * pins, int counter){
  err1[3] = (1. * (counter % 10)-5 )*100/5.;
  writeTemp(pins, err1);
  delay(500);
}

void loop(){
 //doPID(); 
 Serial.println("------" ); 
 testBoard(pins1);
 testBoard(pins2);
 
 //testVoltagRamp(pins1, i);
 //testVoltagRamp(pins2, i);
 //err1[3] = -100;
 //writeTemp(pins1, err1);
 i = i +1;
}

float constrainMap(float x, float in_min, float in_max, float out_min, float out_max)
{
  return constrain((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min,
                    out_min, out_max);
}
