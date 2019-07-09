void initPiIntensities(){
  //this will send the pi init pin a trigger and then
  //send a series of intensities to tell the pi what 
  //values to prepare.
  Serial.println("starting pi intensities");
  Serial.print("state is ");
  Serial.println(state);
  Serial.print("size 1 is ");
  Serial.println(grate_size1);
  Serial.print("size 2 is ");
  Serial.println(grate_size2);
  Serial.print("black level is ");
  Serial.println(black_level);
  Serial.print("altISI is ");
  Serial.println(altISI);
  Serial.print("doOpto is ");
  Serial.println(doOpto);
  digitalWrite(piInitPin, HIGH);
  delay(100);
  //first, send sizes
  sendPiNumber(grate_size1);
  delay(50);
  endSendPiNumber();
  delay(50);
  sendPiNumber(grate_size2);
  delay(50);
  endSendPiNumber();
  delay(50);
  //send the black level
  sendPiNumber(black_level);
  delay(50);
  endSendPiNumber();
  delay(20);
  for (int index = 0; index < (sizeof(outputLevels) / sizeof(int)); index++){
    sendPiNumber(outputLevels[index]);
    delay(50);
    endSendPiNumber();
    delay(20);
  }
  digitalWrite(piInitPin, LOW);
  delay(3000); //let the pi do its thing
}

void sendPiNumber(int num){
  for (byte i=0; i<numPins; i++) {
    byte state = bitRead(num, i);
    digitalWrite(pins[i], state);
  }
  //set pi rec pin high to tell it to look for this info
  digitalWrite(piReceivePin, HIGH);
}

void endSendPiNumber(){
  for (byte i=0; i<numPins; i++) {
    digitalWrite(pins[i], LOW);
  }
  digitalWrite(piReceivePin, LOW);
}
