#include <SoftwareSerial.h>
#include "PacketStruc.h"
#include "Honeywell_RSC.h"
SoftwareSerial pmsSerial(2, 3);

// Macros
#define MAKE_INT(hi,low) (((unsigned char)(hi)<<8)+(unsigned char)(low))

// pins used for the connection with the sensor
// the other you need are controlled by the SPI library):
#define DRDY_PIN      6
#define CS_EE_PIN     7
#define CS_ADC_PIN    8
#define ANALOG_INPUT A0
#define DELAY_PERIOD 100

// create Honeywell_RSC instance
Honeywell_RSC rsc(
  DRDY_PIN,   // data ready
  CS_EE_PIN,  // chip select EEPROM (active-low)
  CS_ADC_PIN  // chip select ADC (active-low)
);

uint8_t  buffer[64];
uint16_t calculated_checksum;
uint16_t pkt_checksum;
uint16_t  pass_count;
volatile double CalibrationValue;
unsigned long time;

void setup() {
  // open SPI communication
  SPI.begin();

  // allowtime to setup SPI
  delay(5);

  // initialse pressure sensor
  rsc.init();

  pinMode(ANALOG_INPUT, INPUT);
  CalibrationValue = rsc.get_pressure()*1000;
  
  // our debugging output
  Serial.begin(9600);
 
  // sensor baud rate is 9600
  pmsSerial.begin(9600);

  // Print header
  //Serial.print("Count_under_0.3um,");Serial.print("Count_under_0.5um,");Serial.print("Count_under_1.0um,");
  //Serial.print("Count_under_2.5um,");Serial.print("Count_under_5.0um,"); Serial.print("Count_under_10.0um");
  //Serial.println();
  
  buffer[32] = 0xAA;
}

void loop() {

  if (buffer[32] != (uint8_t)0xAA){
    Serial.println("BUFFER OVERWRITTEN");
    Serial.print("Expected 0xAA, but got 0x");Serial.println(buffer[32], HEX);
    while(1);
  }
  
  // Check data packet function
  if (!readPMSdata) return;

  // Read data packet and output serial data condition
  else{
    // Compute time in seconds from power on
    time = millis();
    // Read pms data
    pmsSerial.readBytes(buffer, PACKET_SIZE);

    // Serial outputs

    // Time
    Serial.print(time);Serial.print(" ");
    // Pressure
    Serial.print((rsc.get_pressure()*1000-CalibrationValue)/1.1);Serial.print(" ");
    // Analog input (moisture sensor)uncomment line below if analog is to be used    
    //Serial.print((double)analogRead(ANALOG_INPUT));Serial.print(" ");
    // Particles under 0.3 um
    Serial.print((uint16_t)MAKE_INT(buffer[Count03_High],buffer[Count03_Low]));Serial.print(" ");
    // Particles under 0.5 um
    Serial.print((uint16_t)MAKE_INT(buffer[Count05_High],buffer[Count05_Low]));Serial.print(" ");
    // Particles under 1.0 um
    Serial.print((uint16_t)MAKE_INT(buffer[Count10_High],buffer[Count10_Low]));Serial.print(" ");
    // Particles under 2.5 um
    Serial.print((uint16_t)MAKE_INT(buffer[Count25_High],buffer[Count25_Low]));Serial.print(" ");
    // Particles under 5.0 um
    Serial.print((uint16_t)MAKE_INT(buffer[Count50_High],buffer[Count50_Low]));Serial.print(" ");
    // Particles under 10 um
    Serial.print((uint16_t)MAKE_INT(buffer[Count100_High],buffer[Count100_Low]));Serial.println();
    pass_count +=1;
  }
  
}

boolean readPMSdata(void) {
  if (!pmsSerial.available()) return false;
  
  // Read untill 0x42 start byte
  if ((uint8_t)pmsSerial.peek() != 0x42) {
    pmsSerial.read();
    return false;
  }
 
  // Now read all 32 bytes
  if (pmsSerial.available() < PACKET_SIZE) {
    return false;
  }

  pmsSerial.readBytes(buffer, PACKET_SIZE);
  
  // Calculate check sum excluding checksum from buffer
  calculated_checksum = 0;
  for (uint8_t i=0; i<PACKET_SIZE-3; i++) {
    calculated_checksum += (unsigned char)buffer[i];
  }
  
  // Find buffer checksum (packet size is 32)
  pkt_checksum = (uint16_t)MAKE_INT(buffer[PACKET_SIZE-2],buffer[PACKET_SIZE-1]);

  if ((buffer[3]!=0x1C)||(buffer[2]!=0x0)){
    //Serial.println("BUFFER HAS UNEXPECTED LENGTH");
    return false;
  }
  
  if (pkt_checksum!=calculated_checksum){
    for (uint8_t j=0; j<PACKET_SIZE; j++) {
      Serial.print("0x"); Serial.print((unsigned char)buffer[j], HEX); Serial.print(", ");
    }
    Serial.println();
    Serial.println("CHECK SUM ERROR:");
    Serial.print("calculated_checksum:");Serial.println((uint16_t)calculated_checksum, HEX);
    Serial.print("pkt_checksum:");Serial.println((uint16_t)pkt_checksum, HEX);
    return false;
  }
  else return true;
}
