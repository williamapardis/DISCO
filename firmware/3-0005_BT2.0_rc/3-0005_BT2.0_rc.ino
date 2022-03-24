
/*
DISCO II Firmware
This code is flashed on the ATSAMD M4 on the DISCO 3-0005 PCB. This board and firmware handles data trafic from the Samsung table to the internal DISCO hardware via a BLE connection.
Data is aqquired from multiple flow sensors and the PMT appended and send comma delimited to the tablet. Commands from the tablet are used to set a 14bit DAC controlling the three 
parastaltic pumps. 
*/

//included libraries
#include <Wire.h>         //I2C communications
#include <Arduino.h>      //SERCOM routing
#include <SPI.h>          //serial perriferal interface communications
#include <Arduino.h>        // required before wiring_private.h
#include "wiring_private.h" // pinPeripheral() function

//byte manipulation functions
#define lowByte(w) ((uint8_t) ((w) &0xff))  
#define highByte(w) ((uint8_t) ((w) >> 8))

//I2C addresses
#define ADDR_Mot 0x60 //12bit DAC
#define ADDR_Mux 0x70 //I2C multiplexer
#define ADDR_FS  0x08 //flow sensors


//for flow sensor conversion
const float SCALE_FACTOR_FLOW = 1200.0;
const float SCALE_FACTOR_TEMP = 200.0;

//for PMT SERCOM Uart
Uart Serial2 (&sercom1, 11, 10, SERCOM_RX_PAD_0, UART_TX_PAD_2);

//not sure what this does 
void SERCOM1_Handler()
{
  Serial2.IrqHandler();
}



void setup() {

  //shut off on board LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  //reset
  pinMode(5,OUTPUT);
  digitalWrite(5,HIGH);

  //initialize serial UARTs
  Serial.begin(9600);     //USB interface
  Serial1.begin(9600);    //bluetooth
  Serial2.begin(9600);    //PMT interface

  Serial1.println("initializing SERCOM for PMT");
  // Assign pins 10 & 11 SERCOM functionality
  pinPeripheral(10, PIO_SERCOM);
  pinPeripheral(11, PIO_SERCOM);

  //initilize I2C
  Serial1.println("initializing I2C");
  Wire.begin();Serial.println("I2C initialized");

  //set DAC to startup with motors off
  Serial1.println("initializing Motor Control");
  Wire.beginTransmission(ADDR_Mot);
  Wire.write(0x50); //write to DAC EEPROM sequntially
  Wire.write(0x98); //Vref internal,no powerdown,gain 2x, 2.048V at startup
  Wire.write(0x00);
  Wire.write(0x98);
  Wire.write(0x00);
  Wire.write(0x98);
  Wire.write(0x00);
  Wire.write(0x98);
  Wire.write(0x00);
  Wire.endTransmission();
  //motors off
  setMotorSpeed("A2048");

  //flow sensor setup
  Serial1.println("initializing flow sensors");
  Serial.print("Setting up flow sensor... ");
  tcaselect(0);       //select sensor on bus 0
  delay(500);
  flowSensorSetup();
  delay(500);
  tcaselect(1);       //select sensor on bus 1
  delay(500);
  flowSensorSetup();
  Serial.println("flow sensor initialized");

  delay(3000);  //app has time to set up before sending data.
  
  //PMT settings
  Serial1.println("initializing PMT, VA is a valid response... ");
  Serial1.print("setting integration time... ");
  Serial2.write('P');Serial2.write('1');Serial2.write('\r');delay(100);  //integration time
  while(Serial2.available()){Serial1.write(Serial2.read());}
  Serial1.println();
  Serial1.print("setting voltage... ");
  Serial2.write('D');Serial2.write('\r');delay(100);   //votage
  while(Serial2.available()){Serial1.write(Serial2.read());}
  Serial1.println();
  Serial1.print("starting continueous read... ");
  Serial2.write('C');Serial2.write('\r');delay(100);   //start continuous read
  while(Serial2.available()){Serial1.write(Serial2.read());}
  Serial1.println();
  delay(100);
  Serial1.println("PMT ready");

  
  
}

//Global Variables------------------------------------------------------------------------
uint16_t aux_value;
uint16_t sensor_flow_value; 
uint16_t sensor_temp_value;
int16_t signed_flow_value;
int16_t signed_temp_value;

byte aux_crc;
byte sensor_flow_crc;
byte sensor_temp_crc;

float scaled_flow_value0=0,scaled_flow_value1=0;
float scaled_temp_value0=0,scaled_temp_value1=0;  
int avg0=0,avg1=0;
bool FF=true;

char   command[6];
//------------------------------------------------------------------------------------------

void loop() {  

  //aquiring flow sensor data
  delay(10);
  tcaselect(0);       //select sensor on bus 0
  aquireFlow(0);
  delay(10);
  tcaselect(1);       //select sensor on bus 1
  aquireFlow(1);
  avg0++;avg1++;

  //if pmt data available send read it and send averaged flow data along with it
  if(Serial2.available()>3){
   
    String data="";

    //average current flow senor 1 data
    data=String(scaled_temp_value0/float(avg0),1)+','+String(scaled_flow_value0/float(avg0),1)+',';
    scaled_flow_value0=0;scaled_temp_value0=0;avg0=0;

    //average current flow sensor 2 data
    data+=String(scaled_temp_value1/float(avg1),1)+','+String(scaled_flow_value1/float(avg1),1)+',';
    scaled_flow_value1=0;scaled_temp_value1=0;avg1=0;

    //pmt data
    char mybuf[4];
    while(Serial2.available()>3){Serial.println(Serial2.available());Serial2.readBytes(mybuf,4);}
    while(Serial2.available()>0){Serial2.read();} //clear buffer
    data += (uint32_t)mybuf[0] << 24 | (uint32_t)mybuf[1] << 16 | (uint32_t)mybuf[2] << 8 | (uint32_t)mybuf[3];

    //send data
    Serial1.println(data);
    Serial.println(data);
  
  }

  
  while(Serial1.available()){
    setMotorSpeed(Serial1.readStringUntil('\n'));      
  }
  
}



uint16_t a=2048,b=2048,c=2048,d=2048; 

void setMotorSpeed(String com){
    Serial.println(com);
    if(com[0]=='R'){
      Serial.println("reseting");
      digitalWrite(5,LOW);
    }
    else{
      String comTemp = com.substring(1,6);
      uint16_t spd = atoi(comTemp.c_str());
  
      if(spd==0){
        Serial.println("invalid command, motor index (a,b,c or d) followed by 12 bit speed (1 to 4095)");
        return;
      }
      
      if(com[0]=='a'){
          Serial.print("Motor A speed changed to: ");Serial.println(spd);
          a=spd;
      }
      else if(com[0]=='b'){
          Serial.print("Motor B speed changed to: ");Serial.println(spd);
          b=spd;
      }
      else if(com[0]=='c'){
          Serial.print("Motor C speed changed to: ");Serial.println(spd);
          c=spd;
      }
      else if(com[0]=='d'){
          Serial.print("Motor D speed changed to: ");Serial.println(spd);
          d=spd;
      }
      else if(com[0]=='A'){
          Serial.print("All motors speed changed to: ");Serial.println(spd);
          a=spd;b=spd;c=spd;d=spd;
      }
      else if(com[0]=='P'){
          Serial2.write('P');Serial2.write(spd);Serial2.write('\r');delay(100);  //integration time
          Serial.println("setting integration");
      }
      else if(com[0]=='V'){
          Serial2.write('V');Serial2.write(spd);Serial2.write('\r');delay(100);  //integration time
          Serial.println("setting voltage");
      }
      else if(com[0]=='D'){
          Serial2.write('D');Serial2.write('\r');delay(100);
          while(Serial2.available()){Serial1.write(Serial2.read());}
          Serial.println("default");
      }
      else{
          Serial.println("invalid command, motor index (a,b,c or d) followed by 12 bit speed (1 to 4095)");
          Serial.print(com);
          return;
      }
              
      Wire.beginTransmission(ADDR_Mot);
      Wire.write(highByte(a));
      Wire.write(lowByte(a));
      Wire.write(highByte(b));
      Wire.write(lowByte(b));
      Wire.write(highByte(c));
      Wire.write(lowByte(c));
      Wire.write(highByte(d));
      Wire.write(lowByte(d));
      Wire.endTransmission();
  }
    
}









void tcaselect(uint8_t i) {
  
  //Serial.print("Selecting I2C channel: ");Serial.println(i);
  if (i > 7) return;
 
  Wire.beginTransmission(ADDR_Mux);
  Wire.write(1 << i);
  Wire.endTransmission();  
  
}










void flowSensorSetup(){
    int ret;
    
    do {
        // Soft reset the sensor
        Wire.beginTransmission(0x00);
        Wire.write(0x06);
        ret = Wire.endTransmission();
        if (ret != 0) {
            Serial.println("Error while sending soft reset command, retrying...");
            delay(500); // wait long enough for chip reset to complete
        }
    } while (ret != 0);
    Serial.println("RESET Successful");
    
    delay(50);
    // To perform a measurement, first send 0x3608 to switch to continuous
    // measurement mode, then read 3x (2 bytes + 1 CRC byte) from the sensor.
    Wire.beginTransmission(ADDR_FS);
    Wire.write(0x36);
    Wire.write(0x08);
    ret = Wire.endTransmission();
    if (ret != 0) {
        Serial.println("Error during write measurement mode command");
    }
    
    delay(500);
}







void aquireFlow(int SN){
  
  Wire.requestFrom(ADDR_FS, 9);
  if (Wire.available() < 9) {
      Serial.println("Error while reading flow measurement");
  }

  sensor_flow_value  = Wire.read() << 8; // read the MSB from the sensor
  sensor_flow_value |= Wire.read();      // read the LSB from the sensor
  sensor_flow_crc    = Wire.read();
  sensor_temp_value  = Wire.read() << 8; // read the MSB from the sensor
  sensor_temp_value |= Wire.read();      // read the LSB from the sensor
  sensor_temp_crc    = Wire.read();
  aux_value          = Wire.read() << 8; // read the MSB from the sensor
  aux_value         |= Wire.read();      // read the LSB from the sensor
  aux_crc            = Wire.read();

  signed_flow_value = (int16_t) sensor_flow_value;
  signed_temp_value = (int16_t) sensor_temp_value;
  
  if(SN==0){
    scaled_flow_value0 += ((float) signed_flow_value) / SCALE_FACTOR_FLOW;
    scaled_temp_value0 += ((float) signed_temp_value) / SCALE_FACTOR_TEMP;
  }
  if(SN==1){
    scaled_flow_value1 += ((float) signed_flow_value) / SCALE_FACTOR_FLOW;
    scaled_temp_value1 += ((float) signed_temp_value) / SCALE_FACTOR_TEMP;
  }
}
