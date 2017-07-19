const int analogInPin[2] = {A0,A1};  // Analog input pin that the potentiometer is attached to
const int analogOutPin[2] = {9,10}; // Analog output pin that the LED is attached to
//#define PIN_SWITCH 1

int sensor[2] = {0,0};        // value read from the pot
float temp[2] = {0,0};        // value output to the PWM (analog out)
float target[2] = {360,351}; //  
float delta[2] = {0,0};
int outputValue[2] = {0,0};
// Parametrized curve using beta = 4100K and R25 = 15kOhm and R = 6.8 kOhm
float _in[] = {103, 129, 159, 193, 231, 273, 318, 366, 415, 465, 515, 563, 610,
       654, 696, 734, 769, 801, 830, 856, 879, 899, 917, 933, 948, 960,
       971, 981, 990, 997};
float _out[] = {270, 274, 278, 283, 287, 292, 296, 301, 305, 310, 314, 319, 323,
       328, 332, 337, 341, 346, 350, 355, 359, 364, 368, 373, 377, 382,
       386, 391, 395, 400};

void setup() {
  // put your setup code here, to run once:
  // initialize serial communications at 9600 bps:
  Serial.begin(9600);
  
}

void loop() {
  delay(300);
  // read the analog in value:
  sensor[0] = analogRead(analogInPin[0]);
  sensor[1] = analogRead(analogInPin[1]);
  
  // map it to the range of the analog out:
  temp[0] = FmultiMap(sensor[0], _in, _out, 30);
  temp[1] = FmultiMap(sensor[1], _in, _out, 30);
  
  // change the analog out value:
  //analogWrite(analogOutPin, outputValue);
  Serial.print("sensor = ");
  Serial.print(sensor[0]);
  Serial.print(" - ");
  Serial.print(sensor[1]);
  Serial.print("\t output = ");
  Serial.print(temp[0]);
  Serial.print(" - ");
  Serial.println(temp[1]);
  
  delta[0] = temp[0]-target[0]; 
  delta[1] = temp[1]-target[1]; 
  
  if (delta[0] > 0){
    analogWrite(analogOutPin[0],00 );
    Serial.println("\tH0 OFF ");
  } else {
    outputValue[0] = map(delta[0], 0, 1023, 0, 254);
    analogWrite(analogOutPin[0], 254);
    Serial.println("\tH0 On "); 
  }
  if (delta[1] > 0){
    analogWrite(analogOutPin[1],00 );
    Serial.println("\tH1 OFF ");
  } else {
    outputValue[1] = map(delta[1], 0, 1023, 0, 254);
    analogWrite(analogOutPin[1], 254);
    Serial.println("\tH1 On "); 
  }
}

float FmultiMap(float val, float * _in, float * _out, uint8_t size)
{
  // take care the value is within range
  // val = constrain(val, _in[0], _in[size-1]);
  if (val <= _in[0]) return _out[0];
  if (val >= _in[size-1]) return _out[size-1];

  // search right interval
  uint8_t pos = 1;  // _in[0] allready tested
  while(val > _in[pos]) pos++;

  // this will handle all exact "points" in the _in array
  if (val == _in[pos]) return _out[pos];

  // interpolate in the right segment for the rest
  return (val - _in[pos-1]) * (_out[pos] - _out[pos-1]) / (_in[pos] - _in[pos-1]) + _out[pos-1];
}
