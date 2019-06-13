#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>

/* This driver uses the Adafruit unified sensor library (Adafruit_Sensor),
   which provides a common 'type' for sensor data and some helper functions.
   
   To use this driver you will also need to download the Adafruit_Sensor
   library and include it in your libraries folder.

   You should also assign a unique ID to this sensor for use with
   the Adafruit Sensor API so that you can identify this particular
   sensor in any data logs, etc.  To assign a unique ID, simply
   provide an appropriate value in the constructor below (12345
   is used by default in this example).
   
   Connections
   ===========
   Connect SCL to I2C SCL Clock
   Connect SDA to I2C SDA Data
   Connect VDD to 3.3V or 5V (whatever your logic level is)
   Connect GROUND to common ground

   I2C Address
   ===========
   The address will be different depending on whether you leave
   the ADDR pin floating (addr 0x39), or tie it to ground or vcc. 
   The default addess is 0x39, which assumes the ADDR pin is floating
   (not connected to anything).  If you set the ADDR pin high
   or low, use TSL2561_ADDR_HIGH (0x49) or TSL2561_ADDR_LOW
   (0x29) respectively.
    
   History
   =======
   2013/JAN/31  - First version (KTOWN)
*/
   
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);

/**************************************************************************/
/*
    Displays some basic information on this sensor from the unified
    sensor API sensor_t type (see Adafruit_Sensor for more information)
*/
/**************************************************************************/
int piOnPin = 33; //tell pi to turn stim on
int piInitPin = 34; //tell pi to turn stim off
int piReceivePin = 35; //tell pi to receive next trial stim info
const byte numPins = 8;
byte pins[] = {36, 37, 38, 39, 40, 41, 42, 43}; //pins for writing binary info
int piInputPin = 42; //get info from the pi
int piRecOutputPin =44;

void displaySensorDetails(void)
{
  sensor_t sensor;
  tsl.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" lux");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" lux");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" lux");  
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

/**************************************************************************/
/*
    Configures the gain and integration time for the TSL2561
*/
/**************************************************************************/
void configureSensor(void)
{
  /* You can also manually set the gain or enable auto-gain support */
   //tsl.setGain(TSL2561_GAIN_1X);      /* No gain ... use in bright light to avoid sensor saturation */
   tsl.setGain(TSL2561_GAIN_16X);     /* 16x gain ... use in low light to boost sensitivity */
  //tsl.enableAutoRange(true);            /* Auto-gain ... switches automatically between 1x and 16x */
  
  /* Changing the integration time gives you better sensor resolution (402ms = 16-bit data) */
  //tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS);      /* fast but low resolution */
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_101MS);  /* medium resolution and speed   */
  // tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);  /* 16-bit data but slowest conversions */

  /* Update these values depending on what you've set above! */  
  Serial.println("------------------------------------");
  Serial.print  ("Gain:         "); Serial.println("Auto");
  Serial.print  ("Timing:       "); Serial.println("13 ms");
  Serial.println("------------------------------------");
}

void sendPiStimIntensity(int num){
  Serial.println(num);
  for (byte i=0; i<numPins; i++) {
    byte state = bitRead(num, i);
    digitalWrite(pins[i], state);
    Serial.print(state);
  }
  Serial.println(",");
  //set pi rec pin high to tell it to look for this info
  digitalWrite(piReceivePin, HIGH);
}

void endSendPiStimIntensity(){
  for (byte i=0; i<numPins; i++) {
    digitalWrite(pins[i], LOW);
  }
  digitalWrite(piReceivePin, LOW);
}


void sendPiLux(int num){
  //Serial.println(num);
  for (byte i=0; i<numPins; i++) {
    byte state = bitRead(num, i);
    digitalWrite(pins[i], state);
    //Serial.print(state);
  }
  //set pi rec pin high to tell it to look for this info
  digitalWrite(piRecOutputPin, HIGH);
}

void endSendPiLux(){
  for (byte i=0; i<numPins; i++) {
    digitalWrite(pins[i], LOW);
  }
  digitalWrite(piRecOutputPin, LOW);
}
/**************************************************************************/
/*
    Arduino setup function (automatically called at startup)
*/
/**************************************************************************/
void setup(void) 
{
  Serial.begin(9600);
  pinMode(piOnPin, OUTPUT);
  pinMode(piInitPin, OUTPUT);
  pinMode(piReceivePin, OUTPUT);
  pinMode(piRecOutputPin, OUTPUT);
  pinMode(piInputPin, INPUT);
  digitalWrite(piInitPin, LOW);
  digitalWrite(piReceivePin, LOW);
  digitalWrite(piRecOutputPin, LOW);
  for (int i=0; i<numPins; i++){
    pinMode(pins[i], OUTPUT);
    digitalWrite(pins[i], LOW);
  }
  Serial.println("Light Sensor Test"); Serial.println("");
  
  /* Initialise the sensor */
  //use tsl.begin() to default to Wire, 
  //tsl.begin(&Wire2) directs api to use Wire2, etc.
  if(!tsl.begin())
  {
    /* There was a problem detecting the TSL2561 ... check your connections */
    Serial.print("Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  
  /* Display some basic information on this sensor */
  displaySensorDetails();
  
  /* Setup the sensor gain and integration time */
  configureSensor();
  
  /* We're ready to go! */
  Serial.println("");
}

int get_lux(){
  /* Get a new sensor event */ 
  sensors_event_t event;
  tsl.getEvent(&event);
 
  /* Display the results (light is measured in lux) */
  if (event.light)
  {
    Serial.print(event.light); Serial.println(" lux");
  }
  else
  {
    /* If event.light = 0 lux the sensor is probably saturated
       and no reliable data could be generated! */
    Serial.println("Sensor overload");
  }
  return event.light;
}
/**************************************************************************/
/*
    Arduino loop function, called once 'setup' is complete (your own code
    should go here)
*/
/**************************************************************************/
void loop(void) 
{  
  digitalWrite(piInitPin,HIGH);
   Serial.println("send init");
   delay(2000);
   int outputLevels[] = {0,5, 10, 15,20, 25,30,35, 40,45, 50,55, 60, 65,70, 75,80, 85,90,95, 100, 105,110,115,120, 125,130,135, 140,145, 150,155, 160, 165, 170,175, 180, 185,190,195, 200, 205,210,215, 220,225, 230,235, 240,245 ,250,255};
   for (int index = 0; index < (sizeof(outputLevels) / sizeof(int)); index++){
    sendPiStimIntensity(outputLevels[index]);
    delay(50);
    endSendPiStimIntensity();
    delay(20);
  }
  delay(2000);
   Serial.println("send done");
   digitalWrite(piInitPin,LOW);
    delay(3000);
  for (int index = 0; index < (sizeof(outputLevels) / sizeof(int)); index++){
    sendPiStimIntensity(outputLevels[index]);
    delay(150);
    endSendPiStimIntensity();
    Serial.println(outputLevels[index]);
    digitalWrite(piOnPin, HIGH);
    delay(400);
    int read_val = 0;
    read_val = int(get_lux());
    sendPiLux(read_val);
    delay(100);
    endSendPiLux();
    delay(100);
    digitalWrite(piOnPin, LOW);
  }
  delay(200000);
}

