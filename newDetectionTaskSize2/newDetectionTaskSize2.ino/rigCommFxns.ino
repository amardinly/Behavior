
int getNextStimIdx(){
    //for daq communication
    //int wantedval = stimVals[thisTrialNumber+1];
    //for (int i=0; i < (sizeof(outputLevels) / sizeof(int)); i++) {
    //     if (wantedval == outputLevels[i]) {
    //       nextStimIdx = i;
    //       break;
    //     }
    //}
    //nextStimIdx++; //add one bc matlab indexing is like that
    //return nextStimIdx;
    return 0;
}

void doPulsingStimIdx(){
  //use global variables to handle pulsing for sending stim idx
  //this is just used for daq comm
  if (millis() >= nextPulseTime && pulsesSent < nextStimIdx){
      if (pulsing == true){ //if its currently on, turn it off
        digitalWrite(digOutPin, LOW);
        nextPulseTime = millis() + 2;
        pulsesSent++;
        pulsing = false;
        if (pulsesSent == nextStimIdx){
          donePulsing = true;
        }
      } else{
        digitalWrite(digOutPin, HIGH);
        nextPulseTime = millis()+2;
        pulsing = true;      
      }
  }
}


void sendBehaviorOutcome(){
      //for daq comm, send pulses
      if (stimVals[thisTrialNumber] == 0 && catchFA == true) {
         for (int pulses = 0; pulses < 1; pulses++){
            digitalWrite(digOutPin, HIGH);
            delay(4);
            digitalWrite(digOutPin, LOW);
            delay(4);
         }
      }
      if (stimVals[thisTrialNumber] == 0 && catchFA == false) {
         for (int pulses = 0; pulses < 2; pulses++){
            digitalWrite(digOutPin, HIGH);
            delay(4);
            digitalWrite(digOutPin, LOW);
            delay(4);
          }
      }
      if (stimVals[thisTrialNumber] > 0 && trialRewarded == false) {
         for (int pulses = 0; pulses < 3; pulses++){
            digitalWrite(digOutPin, HIGH);
            delay(4);
            digitalWrite(digOutPin, LOW);
            delay(4);
         }
      }

      if (stimVals[thisTrialNumber] > 0 && trialRewarded == true) {
         for (int pulses = 0; pulses < 4; pulses++){
            digitalWrite(digOutPin, HIGH);
            delay(4);
            digitalWrite(digOutPin, LOW);
            delay(4);
         }
      }
}
