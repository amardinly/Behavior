void checkSerial(){
  //check serial for start/stop or prompt info
  if (Serial.available()) {
      val = Serial.read();
      Serial.println(val);
      if (val == '1')  {
        isRunning = true;
        daqReady = true;
        if (init_pi == false){
          initPiIntensities();
          init_pi = true;
        }
        //nextTrialStart = nextTrialStart + 5000;
      }
  
      if (val == '0') {
        isRunning = false;
        analogWrite(magnetPin, 0); // make sure mag and water are closed
        digitalWrite(waterPin, LOW);
        digitalWrite(piFAPin, LOW);
      }

      if (val == '2' & isRunning == false) {
        digitalWrite(waterPin, HIGH);
        delay(valveOpenTime*2);
        digitalWrite(waterPin, LOW);
        if (nextTrialStart<=millis()+1500) {
          nextTrialStart = millis() + 1500; 
        }
      }
      if (val == '3' & isRunning == false) {
        if (visual==true){
          sendPiNumber(126);
          delay(50);
          turnVisOn();
          delay(200);
          turnVisOff();
        }
        analogWrite(magnetPin,  250);
        delay(300);
        analogWrite(magnetPin,  0);
        stimEndTime = millis() + 300; 
        if (nextTrialStart<=millis()+1500) {
          nextTrialStart = millis() + 1500; 
        }
      }
      if (val=='4' & visual==true){
        initPiIntensities();
      }
  }
  //if debugging, even if serial isn't present, start
  if (debug == true){ 
    isRunning = true;
  }
}


void sendSerial(){
  Serial.print(millis());//millis() - trialStartTime);
  Serial.print(",");
  Serial.print(thisTrialNumber);
  Serial.print(",");
  Serial.print(trialRewarded);
  Serial.print(",");
  //actually check if lickport is high each time
  Serial.print(isLicking());
  Serial.print(",");
  Serial.print(stimVals[thisTrialNumber]);
  Serial.print(",");
  Serial.print(isResponseWindow);
  Serial.print(",");
  Serial.print(magnetOn);
  Serial.print(",");
  Serial.print(waterPortOpen);
  Serial.print(",");
  Serial.print(falseAlarm);
  Serial.print(",");
  Serial.println(sizeVals[thisTrialNumber]);
}

void establishContact() {
  //handshake with processing and then get the state, grate_size, and then black_level
  while (Serial.available() <= 0) {
    Serial.println("A");
    delay(300);
  }
  
  int value;
  while ( Serial.available()){
    char ch = Serial.read();
    Serial.println(ch);
    if(ch >= '0' && ch <= '9') // is this an ascii digit between 0 and 9?
       value = (value * 10) + (ch - '0'); // yes, accumulate the value
    else if (ch=='z') // this assumes any char not a digit or minus sign terminates the value
    {
       grate_size1 = value;
       value = 0; // reset value to 0 ready for the next sequence of digits
    }
    else if (ch=='c') // this assumes any char not a digit or minus sign terminates the value
    {
       grate_size2 = value;
       value = 0; // reset value to 0 ready for the next sequence of digits
    }
    else if (ch=='b') // this assumes any char not a digit or minus sign terminates the value
    {
       black_level = value;
       value = 0; // reset value to 0 ready for the next sequence of digits
    }
    else if (ch=='s'){
      state = value;
      value = 0;
    }
    else if (ch=='x'){
      value=0;
    }
    Serial.println(value);
  }
  
  Serial.println("Q");
  Serial.println(black_level);
}
