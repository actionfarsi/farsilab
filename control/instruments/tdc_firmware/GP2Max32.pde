#include <SPI.h>
#include <stdio.h>
#define BUFFER_SIZE 2048

const byte READ = 0xB0;     // Read command
const byte WRITE = 0x80;    // Write command
const byte INIT = 0x70;  // Init opcode command
const byte RESET = 0x50;  // Reset opcode command

// pins used for the connection with the sensor
// the other you need are controlled by the SPI library):
const int dataReadyPin = 2;
const int resetBoardPin = 48;
const int slaveSelectPin = 53;
const int debugPin = 47;
const int vccPin = 14;
volatile int state = LOW;
bool bufferFlag = false;
bool histogramFlag = false;
int histogramRange = 8;
int histogramChannel = 0;
bool readCh2 = false;

long volatile timeData[BUFFER_SIZE];
long volatile timeData2[BUFFER_SIZE];
char code[16];
//int dataRead = 0

void setup() {                
  Serial.begin(38600*4*4);
  //Serial.bufferUntil('\n');
  
  // start the SPI library:
  SPI.begin();
  // Configure SPI transmission
  SPI.setDataMode(1);
  SPI.setBitOrder(MSBFIRST);
  pinMode(slaveSelectPin, OUTPUT);  // Set the Slave Selector pin
  digitalWrite(slaveSelectPin, HIGH);
  
  // initalize the  data ready and other pins:
  // pinMode(dataReadyPin, INPUT);
  
  attachInterrupt(0, readFromTDC, FALLING);   // Set interupt function
  pinMode(debugPin, OUTPUT);
  
  // initialize the digital pin as an output.
  // Pin 13 has an LED connected on most Arduino boards:
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);    // set the LED off
  
  initTDC();
}

void initTDC(){
  
  SPI.transfer(RESET);
  
  //Configure GP2:
  writeRegister(0x00, 0x00064012);
  writeRegister(0x01, 0x10010034); // reg1
  //writeRegister(0x01, 0x90090034); // reg2
  writeRegister(0x02, 0xe0000056); // Config reg 2
  writeRegister(0x03, 0x38000078); // Config reg 3
  writeRegister(0x04, 0x0000009A); // Config reg 4
  writeRegister(0x05, 0x00000078); // Config reg 5
  //writeRegister(0x06, 0x00006190); // Config reg 6
  
  
  //digitalWrite(resetBoardPin, LOW);          // reset board
  //digitalWrite(resetBoardPin, HIGH);          // reset board
  
  SPI.transfer(INIT);
  delay(10);
  
  // Init the buffer
  for (int i = 0; i<BUFFER_SIZE; i++){
    timeData[i] = 0;
    timeData2[i] = 0;
  }
}

void loop() {
//digitalWrite(13, LOW);   // set the LED off
  if (Serial.available()){
    //noInterrupts();
    
    detachInterrupt(0);   // Set interupt function
    serialEvent();
    attachInterrupt(0, readFromTDC, FALLING);   // Set interupt function
    //interrupts();
    //digitalWrite(13, LOW);    // set the LED off
    Serial.flush();
  }
}

long reg = 0;
long volatile reg2 = 0;


void readFromTDC() {
  //digitalWrite(13, HIGH);   // set the LED on
  if (timeData[0] >= BUFFER_SIZE-10) {
    bufferFlag = true;
    return;
  }
  noInterrupts();
  // Get pointer
  reg2 = readRegister(0x04) >> 16;  // Read Status
  
  if (histogramFlag) {
    histogramChannel = 0x7f& readRegister(reg2) >> histogramRange;
    timeData[0]++;
  }
  
  else {
    // Read Status
    if (readCh2) {
        // Check if Timeout
        if ( (reg2 & 0x200) == 0) {
            // No Timeout, measure everything
            writeRegister(0x01, 0x01090034); // reg1
            //for (int i = 0; i < 5; i++) { i == 1;}
            reg2 = readRegister(0x04) >> 16;  // Read Status
            timeData[timeData[0]+1] = readRegister((reg2-1)% 4);
            
            
            writeRegister(0x01, 0x09090034); // reg2
            //for (int i = 0; i < 5; i++) { i == 1;}
            reg2 = readRegister(0x04) >> 16;  // Read Status
            timeData2[timeData[0]+1] = readRegister( (reg2-1)% 4);
            
        }
        else {
            //Timeout, measure only the one that clicked
            if ( (reg2 & 0x038) != 0) {
                writeRegister(0x01, 0x01090034); // reg1
                //writeRegister(0x01, 0x01090034); // reg1
                //for (int i = 0; i < 50; i++) { i == 1;}
                reg2 = readRegister(0x04) >> 16;  // Read Status
            
                timeData[timeData[0]+1] = readRegister((reg2-1)% 4);
                timeData2[timeData[0]+1] = 0xffffff;
            }
            else if ( (reg2 & 0x1c0) != 0) {
                writeRegister(0x01, 0x09090034); // reg2
                
                //for (int i = 0; i < 50; i++) { i == 1;}
                reg2 = readRegister(0x04) >> 16;  // Read Status
                timeData[timeData[0]+1] = 0xffffff;
                timeData2[timeData[0]+1] = readRegister((reg2-1)% 4);
            }
            else {
                timeData[timeData[0]+1] = 0xffffff;
                timeData2[timeData[0]+1] = 0xffffff;
                
            }
            
        }
        timeData[0]++;
        timeData2[0]++;
        
        
    }
    else {
        timeData[timeData[0]+1] = readRegister( (reg2-1) % 4);
        ++timeData[0];
    }
    
  }
  
  //digitalWrite(resetBoardPin,HIGH);
  //delay(1);
  //digitalWrite(resetBoardPin,LOW);
  
  // Init
  digitalWrite(slaveSelectPin,LOW);
  SPI.transfer(INIT);
  
  digitalWrite(slaveSelectPin,HIGH);
  interrupts();
}

// Command Selection
void serialEvent(){
  readLine(code);
  //noInterrupts();
  switch (code[0]) {
    case 'a':  // TEST
        Serial.write("T2D Board");
        if (readCh2)
            Serial.write("\n Ch2 Active");
        //sprintf(code, "%d", timeData[0]);
        //Serial.write(code);
        digitalWrite(13, LOW);   // set the LED on
        break;
    case 'w':  // Write Register 'w' + addr + 4 byte
        reg = code[2];
        reg = (reg << 8) | code[3];
        reg = (reg << 8) | code[4];
        reg = (reg << 8) | code[5];
        writeRegister(code[1], reg);
        break;
    case '1':
        readCh2 = false;
        timeData[0] = 0;
        timeData2[0] = 0;
        break;
    case '2':
        readCh2 = true;
        timeData[0] = 0;
        timeData2[0] = 0;
        break;
    case 'r':  // Request to read the measurement buffer
        
        sendBuffer();
        break;
    case 's':  // Read register  's' + a
        reg = readRegister(code[1]);
        Serial.write((byte*) &reg, 4);
        break;
    case 't':  // Read status and register
        reg = readRegister(0x04);  // Read Status
        Serial.write((byte*)&reg, 4);
        reg = readRegister(0x05);  // Read Reg1 (last 8 bits)
        Serial.write((byte*)&reg, 4);
        break;
    case 'p':  // Re-set board
        timeData[0] = 0;
        digitalWrite(resetBoardPin,HIGH); 
        delay(1);
        digitalWrite(resetBoardPin,LOW);
        digitalWrite(slaveSelectPin,LOW);
        //SPI.transfer(RESET);
        delay(1);
        SPI.transfer(INIT);
        digitalWrite(slaveSelectPin,HIGH);
        break;
    case 'h':  // Histogram mode
        histogramFlag = !histogramFlag;
        break;
        
  };
  //interrupts();
}

void readLine(char* buffer) {
  delay(8);
  // send data only when you receive data:
  for (int i = 0; Serial.available()>0; i++) {
    // read the incoming byte:
    buffer[i] = Serial.read();
  } 
}

// Send the entire readBuffer through USB
void sendBuffer() {
    
   //noInterrupts();
   if (timeData[0] > 0) {
        Serial.write((byte*) &timeData, (int(timeData[0])+1)*sizeof(long));
        if (readCh2) {
            Serial.write((byte*) &timeData2, (int(timeData2[0])+1)*sizeof(long));
            timeData2[0] = 0;
        }
        timeData[0] = 0;
   }
   bufferFlag = false;
   //interrupts();
   digitalWrite(slaveSelectPin,LOW);
   
   SPI.transfer(INIT);
   digitalWrite(slaveSelectPin,HIGH);
}

long readStatus()  {
  byte inByte = 0;           // incoming byte from the SPI
  long result = 0;   // result to return
  //Serial.print(thisRegister, BIN);
  //Serial.print("\t");
  // SCP1000 expects the register name in the upper 6 bits
  // of the byte. So shift the bits left by two bits:
  //thisRegister = thisRegister << 2;
  // now combine the address and the command into one byte
  byte dataToSend = 0x04 | READ;
  //Serial.println(thisRegister, BIN);
  // take the chip select low to select the device:
  //digitalWrite(chipSelectPin, LOW);
  // send the device the register you want to read:
  SPI.transfer(dataToSend);
  delay(1);
  result = SPI.transfer(0x00);
  result = result << 8;

  inByte = SPI.transfer(0x00);
  result = result | inByte;
  result = result << 8;
  
  return (result);
}

//Read from or write to register from the SCP1000:
long readRegister(byte thisRegister) {
  byte inByte = 0;           // incoming byte from the SPI
  long result = 0;   // result to return
  //Serial.print(thisRegister, BIN);
  //Serial.print("\t");
  // SCP1000 expects the register name in the upper 6 bits
  // of the byte. So shift the bits left by two bits:
  //thisRegister = thisRegister << 2;
  // now combine the address and the command into one byte
  byte dataToSend = thisRegister | READ;
  //Serial.println(thisRegister, BIN);
  // take the chip select low to select the device:
  digitalWrite(slaveSelectPin,LOW);
  
  // send the device the register you want to read:
  SPI.transfer(dataToSend);
  result = SPI.transfer(0x00);
  if (result != 0) digitalWrite(debugPin,HIGH); 
  result = result << 8;
  
  inByte = SPI.transfer(0x00);
  if (inByte != 0) digitalWrite(debugPin,HIGH); 
  result = result | inByte;
  result = result << 8;
  
  inByte = SPI.transfer(0x00);
  if (inByte != 0) digitalWrite(debugPin,HIGH); 
  result = result | inByte;
  result = result << 8;
  
  inByte = SPI.transfer(0x00);
  if (inByte != 0) digitalWrite(debugPin,HIGH); 
  result = result | inByte;
  digitalWrite(slaveSelectPin,HIGH);
  // return the result:
  return(result);
}

long readRegisterRev(byte thisRegister) {
  byte inByte = 0;           // incoming byte from the SPI
  long result = 0;   // result to return
  //Serial.print(thisRegister, BIN);
  //Serial.print("\t");
  // SCP1000 expects the register name in the upper 6 bits
  // of the byte. So shift the bits left by two bits:
  //thisRegister = thisRegister << 2;
  // now combine the address and the command into one byte
  byte dataToSend = thisRegister | READ;
  //Serial.println(thisRegister, BIN);
  // take the chip select low to select the device:
  digitalWrite(slaveSelectPin,LOW);
  
  // send the device the register you want to read:
  SPI.transfer(dataToSend);
  result = SPI.transfer(0x00);
  if (result != 0) digitalWrite(debugPin,HIGH); 
  
  
  inByte = SPI.transfer(0x00);
  if (inByte != 0) digitalWrite(debugPin,HIGH); 
  result = result | inByte << 8;
  
  
  inByte = SPI.transfer(0x00);
  if (inByte != 0) digitalWrite(debugPin,HIGH); 
  result = result | inByte<< 16;
  
  
  inByte = SPI.transfer(0x00);
  if (inByte != 0) digitalWrite(debugPin,HIGH); 
  result = result | inByte << 24;
  digitalWrite(slaveSelectPin,HIGH);
  // return the result:
  return(result);
}
//Sends a write command to SCP1000

void writeRegister(byte thisRegister, long thisValue) {

  byte dataToSend = thisRegister | WRITE;
  byte bufferByte;
  
  //digitalWrite(resetBoardPin, LOW);
  digitalWrite(slaveSelectPin,LOW);
  SPI.transfer(dataToSend); //Send register location
  
  bufferByte = thisValue >> 24;
  SPI.transfer(bufferByte);  //Send value to record into register
  bufferByte = thisValue >> 16;
  SPI.transfer(bufferByte);  //Send value to record into register
  bufferByte = thisValue >> 8;
  SPI.transfer(bufferByte);  //Send value to record into register
  bufferByte = thisValue;
  SPI.transfer(bufferByte);  //Send value to record into register
  
  digitalWrite(slaveSelectPin,HIGH);
  //digitalWrite(resetBoardPin, HIGH);
  

  // take the chip select high to de-select:
  // digitalWrite(chipSelectPin, HIGH);
}
