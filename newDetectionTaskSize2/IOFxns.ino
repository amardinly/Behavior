
bool isLicking(){    
//get whether or not mouse is licking
//sign of the signal is inverted depending on detector
  bool lick=false;
  if (Rig==false){
    if(digitalRead(lickportPin) == LOW){
      lick = true;
    }
  }else if (digitalRead(lickportPin) == HIGH ){
      lick = true;
  }
  return lick;
}

bool isDaqReady(){
  bool dR = false;
  if (digitalRead(readyToGoPin)==HIGH) {
    dR = true;
  } else{
    dR = false;
  }
  
  //whether it just became ready or we're still waiting, still want to add 500ms
  if (nextTrialStart<=millis()+500) {
    nextTrialStart = millis() + 500; 
  }
  return dR
}

void turnLEDOn(){
  //define later 
  return;
}

void turnLEDOff(){
  return;
}

void turnWaterOffOnTime(){
  // close the water if its time to!
  if (millis() >= valveCloseTime && waterPortOpen == true) {
      digitalWrite(waterPin, LOW); //close the water
      waterPortOpen = false;
  }
}

void turnWaterOn(){
  digitalWrite(waterPin, HIGH); //open the water
  valveCloseTime = millis() + valveOpenTime; //mark time to close valve
  trialRewarded = true;
  cumRewards++;
  waterPortOpen = true;
}


void turnTimeOutSignalOffOnTime(){
  // close the water if its time to!
  if (millis() >= timeOutSignalEnd && timeOutSignalOn == true) {
      digitalWrite(piFAPin, LOW); //close the water
      timeOutSignalOn = false;
  }
}


void turnTimeOutSignalOn(){
  if (do_timeout==true){
    //digitalWrite(piFAPin, HIGH); //open the water
    
    tone(8, 6048, timeOutToneTime);
    timeOutSignalEnd = millis() + timeOutSignalTime; //mark time to stop signal
    //generateNoiseSound();
    timeOutSignalOn = true;
  }
}

void turnStimOn(){
  if (visual==true){turnVisOn();}
  else{turnMagOn();}
}

void turnStimOff(){
  if (visual==true){turnVisOff();}
  else{turnMagOff();}
}

void turnMagOn(){
  analogWrite(magnetPin,  stimVals[thisTrialNumber]);  // put voltage on the magnet
  digitalWrite(stimIndicatorPin,HIGH);
  magnetOn = true; //for serial
}

void turnMagOff(){
  analogWrite(magnetPin,  0);  // put voltage on the magnet
  digitalWrite(stimIndicatorPin,LOW);
  magnetOn = false; //for serial
}

void turnVisOn(){
  magnetOn = true;
  digitalWrite(piOnPin, HIGH);
  digitalWrite(stimIndicatorPin, HIGH);
}

void turnVisOff(){
  magnetOn = false;
  digitalWrite(piOnPin, LOW);
  digitalWrite(stimIndicatorPin, LOW);
}

