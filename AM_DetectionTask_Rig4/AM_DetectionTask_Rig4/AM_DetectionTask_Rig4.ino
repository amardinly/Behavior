int state = 2;
// state1 = autorreward (auto)
// state2 = add catch trials  (S2)
// state3 = pyschometric curve (S3)
// state4 = weighted psy curve (S4)
bool Rig = false;
bool synch = false;
bool visual = false;


bool autoReward;
int outputLevels[12];
int outputWeights[12];



int magOnTime = 100;  //duration of magnet on time
int valveOpenTime = 50; //millis that the H20 valve is open
int lickResponseWindow = 1000;//amount of time mice have to response
int responseDelay = 400;  //time between stim onset and answer period
int preTrialNoLickTime = 2000;// no licks before trial or we tgrigger a false alarm
int timeOutDurationMin = 5000;  
int timeOutDurationMax = 8000;  

//Specify pins
int lickportPin = 5;
int waterPin = 9;  
int magnetPin = 11;
int LEDpin = 3;
int triggerPin = 12;
int analogPin = 3;
int readyToGoPin = 4;
int digOutPin = 7;
int stimIndicatorPin = 13;

//set the visual pins
int piOnPin = 31; //tell pi to turn stim on
int piInitPin = 32; //tell pi to turn stim off
int piReceivePin = 33; //tell pi to receive next trial stim info
const byte numPins = 8;
byte pins[] = {34, 35, 36, 37, 38, 39, 40, 41}; //pins for writing binary info
int piInputPin = 42; //get info from the pi

//init vars
int thisTrialNumber = 0;
bool stimTime = false;
bool trialRunning = false;
bool lickOccured = false;
bool isResponseWindow = false;
bool initTrial = true;
bool trialRewarded = false;
bool falseAlarm = false;
bool magnetOn = false;
bool waterPortOpen = false;
bool isRunning = false;
bool debug = false;
bool daqReady = true;
bool catchFA = false;
bool pulsing = false;

int valveCloseTime = 0;  
int nextTrialStart = 5000;  //5 sec baseline before we start stuff
int turnOffStim = 0;
int turnOffResponseWindow = 0;
int cumRewards = 0;
char val;  //data received from serial port


//Init Exp Defaults
int isiMin = 3000;//as in petersen paper
int isiMax = 8000;//as in petersen paper
int trialNumber = 1000;  // num trials to allow
int trialStartTime = 2000;
int ISIDistribution[1050];  ///pad extra to prevent errors
int stimVals[1050];
int stopAfter_n_rewards = 10000;  //dont water that mouse too much!
int stimDelayStart = 50;  // send a trigger to the DAQ 50 ms before stimulus
int stimStartTime = 0;
int stimEndTime = 0;
int rewardPeriodStart =0;
int rewardPeriodEnd = 0;
int lickCounter = 0;
int pulsesSent = 0;
int nextPulseTime = 0;
int nextStimIdx = 0;
bool donePulsing = false;

void chooseParams() {
      if (state==1) {
          autoReward = true;
          outputLevels[0] = 250;
          if (visual==true){
            outputLevels[0] = 126;
          }
          outputWeights[0] = 1;
      }
      if (state==2) {
          autoReward = false;
          outputLevels[0] = 0;
          outputLevels[1] = 250;
          if (visual==true){
            outputLevels[1] = 126;
          } 
          outputWeights[0] = 1;
          outputWeights[1] = 4;
      }
      if (state==3) {
          autoReward = false;
          int theLevels[8]={0,60,100,130,160,190,220,250};
          int theWeights[8] = {1, 1, 1, 1, 1, 1,1,1};
          if (visual==true){
            int theLevels[8]={0,20,  35,  50,   80, 95,  110,   125};//{0,60,100,130,160,190,220,250};
            int theWeights[8] = {1, 1, 1, 1, 1, 1};
          }
          for (int index = 0; index < (sizeof(theWeights) / sizeof(int)); index++){
            outputLevels[index] = theLevels[index];
            outputWeights[index] = theWeights[index];
          }
      }
}

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  pinMode(magnetPin, OUTPUT);
  pinMode(waterPin, OUTPUT);
  pinMode(LEDpin, OUTPUT);
  pinMode(lickportPin, INPUT);  // OR INTERRUPT
  analogWrite(magnetPin, 0); // make sure mag and water are closed
  digitalWrite(waterPin, LOW);
  pinMode(triggerPin, OUTPUT);
  pinMode(analogPin,OUTPUT);
  pinMode(readyToGoPin,INPUT);
  pinMode(digOutPin,OUTPUT);
  pinMode(stimIndicatorPin,OUTPUT);
  pinMode(piOnPin, OUTPUT);
  pinMode(piInitPin, OUTPUT);
  pinMode(piReceivePin, OUTPUT);
  pinMode(piInputPin, INPUT);
  for (int i=0; i<numPins; i++){
    pinMode(pins[i], OUTPUT);
  }
  
  chooseParams();  populateTrials();
  
  if (debug == false) {
     establishContact();
  }
  if (visual == true){
    initPiIntensities();
  }
  thisTrialNumber = 0;//cant figure out where or how this gets reset....but this fixes it
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.println("A");
    delay(300);
  }
}

void initPiIntensities(){
  //this will send the pi init pin a trigger and then
  //send a series of intensities to tell the pi what 
  //values to prepare.
  digitalWrite(piInitPin, HIGH);
  for (int index = 0; index < (sizeof(outputLevels) / sizeof(int)); index++){
    sendPiStimIntensity(outputLevels[index]);
    delay(30);
    endSendPiStimIntensity();
    delay(20);
  }
  digitalWrite(piInitPin, LOW);
}

void sendPiStimIntensity(int num){
  for (byte i=0; i<numPins; i++) {
    byte state = bitRead(num, i);
    digitalWrite(pins[i], state);
    Serial.print(state);
  }
  //set pi rec pin high to tell it to look for this info
  digitalWrite(piReceivePin, HIGH);
}

void endSendPiStimIntensity(){
  for (byte i=0; i<numPins; i++) {
    digitalWrite(pins[i], LOW);
  }
  digitalWrite(piReceivePin, LOW);
}

void doPulsingStimIdx(){
  //use global variables to handle pulsing for sending stim idx
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

int getNextStimIdx(){
    int wantedval = stimVals[thisTrialNumber+1];
    for (int i=0; i < (sizeof(outputLevels) / sizeof(int)); i++) {
         if (wantedval == outputLevels[i]) {
           nextStimIdx = i;
           break;
         }
    }
    nextStimIdx++; //add one bc matlab indexing is like that
    return nextStimIdx;
}
    
void checkSerial(){
  if (Serial.available()) {
      val = Serial.read();
      if (val == '1')  {
        isRunning = true;
        daqReady = true;
        //nextTrialStart = nextTrialStart + 5000;
      }
  
      if (val == '0') {
        isRunning = false;
        analogWrite(magnetPin, 0); // make sure mag and water are closed
        digitalWrite(waterPin, LOW);
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
        analogWrite(magnetPin,  250);
        delay(300);
        analogWrite(magnetPin,  0);
        stimEndTime = millis() + 300; 
        if (nextTrialStart<=millis()+1500) {
          nextTrialStart = millis() + 1500; 
        }
      }
  }
  //if debugging, even if serial isn't present, start
  if (debug == true){ 
    isRunning = true;
  }
}

void sendBehaviorOutcome(){
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

void startTrial(){
      if (Rig == true && synch == true) {
        Serial.println("hey hey");
        daqReady = false;
      }   
      thisTrialNumber=thisTrialNumber + 1;
          
      //SEND TRIGGER TO DAQ
      digitalWrite(triggerPin,HIGH); 
      getNextStimIdx(); //will change a global correctly
    
      //SET TIMER FOR STIMULUS ON
      stimStartTime = millis() + stimDelayStart; 
      stimEndTime = stimStartTime + magOnTime; 
      //TIMER FOR PULSING
      nextPulseTime = millis() + stimDelayStart;
      //SET TIMER FOR REWARD PERIOD START
      rewardPeriodStart = stimEndTime + responseDelay;
      //SET TIMER FOR REWARD PERIOD END
      rewardPeriodEnd = rewardPeriodStart + lickResponseWindow;
      trialStartTime = millis();
      if (visual==true){
        sendPiStimIntensity(stimVals[thisTrialNumber]);     
      }
}

void resetTrial(){
  trialRewarded = false;
  catchFA = false;
  pulsesSent = 0;
  nextStimIdx = 0;
  donePulsing = false;
  nextTrialStart = millis() + ISIDistribution[thisTrialNumber]; //+1000;  // set time for next trial start  
}


//get whether or not mouse is licking
bool isLicking(){
  bool lick=false;
  if (Rig==false){
    if(digitalRead(lickportPin) == LOW) {
      lick = true;
    }
  }else if (digitalRead(lickportPin) == HIGH ){
      lick = true;
  }
  return lick;
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

// the loop function runs over and over again forever
void loop() {
  checkSerial();
   
  //end if we've exceeded the total number of rewards allowed
  if (cumRewards >= stopAfter_n_rewards) {
    isRunning = false;   
  }

  //if its running, do trial things.
  if (isRunning == true) {
      //first, begin in the ISI stage
      while (millis() < nextTrialStart || daqReady==false){
        falseAlarm = false;  //reset this 
        lickOccured = isLicking();
        //if daq is not yet ready, check if ready
        if (daqReady == false){
          if (digitalRead(readyToGoPin)==HIGH) {
            daqReady = true;
          }
          //whether it just became ready or we're still waiting, still want to add 500ms
          if (nextTrialStart<=millis()+500) {
            nextTrialStart = millis() + 500; 
          }
        }
        //check if a false alarm occured, act accordingly
        if (nextTrialStart - (millis()) < preTrialNoLickTime && lickOccured == true) {
                nextTrialStart = nextTrialStart + random(timeOutDurationMin,timeOutDurationMax);
                falseAlarm = true;
        }
        //talk to serial at the end of each loop, and check on serial too
        sendSerial();
        checkSerial();
      }

      startTrial(); // initialize trial
      

      //then wait for the stimulus start
      while (millis()<=stimStartTime){
        sendSerial();
      }
      
      digitalWrite(triggerPin,LOW); //end trigger
      if (visual==true){
        turnVisOn();
        endSendPiStimIntensity();
      } else{
        turnMagOn(); //start mag
      }
      
      while (millis() < stimEndTime) { //during stim presentation
        sendSerial();
        if (Rig==true){
          doPulsingStimIdx();
        }
      }

      if (visual==true){
        turnVisOff();
      } else{
        turnMagOff();
      }

      //then wait for the reward period
      while (millis() < rewardPeriodStart){
        sendSerial();
        if (Rig==true){
          doPulsingStimIdx();
        }
      }

      //then begin the reward period
      isResponseWindow = true;
      //if autoreward, begin giving water
      if (autoReward == true){
        turnWaterOn();
      }
      //handle the reward window
      while ((millis()>= rewardPeriodStart) && (millis()<rewardPeriodEnd))  {
          if (autoReward == false && trialRewarded == false){
            if (isLicking()==true){
              if (stimVals[thisTrialNumber]>0){
                turnWaterOn();
              } else {
                catchFA = true;
              }
            }
          }
          if (Rig==true){
            doPulsingStimIdx();
          }
          turnWaterOffOnTime();
          sendSerial();
      }
      isResponseWindow = false;
      sendSerial();
      //make sure we finished sending mag stim idx pulses
      while (donePulsing==false && Rig==true){
        doPulsingStimIdx();
      }

      //send behavior outcome triggers 1=FA,2=CR,3=MS,4=HT
      if (Rig==true){
        sendBehaviorOutcome();
      }

      resetTrial(); 
      
  }
  sendSerial();
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
  Serial.println(falseAlarm);
}
void populateTrials() {
  int arraySum;
  arraySum = 0;
  int output_size = 0;
  for (int index = 0; index < (sizeof(outputWeights) / sizeof(int)); index++){
    if (outputWeights[index] != 0){
      output_size++;
    }
  }
  for (int index = 0; index < output_size; index++){
    arraySum += outputWeights[index];
  }
  //populate an array containing all the necessary duplicatses...
  int weightedOutputs[arraySum];
  int i = 0;
  for (int n = 0; n < output_size; n++) {
    for (int k = 0; (k < outputWeights[n]); k++) {

      weightedOutputs[i] = outputLevels[n];
      i++;
    }
  }

  i = 0;
  int arrLen = sizeof(weightedOutputs) / sizeof(int);
  while (i < trialNumber) {
    bubbleUnsort(weightedOutputs, arrLen);       //randomize the weighted trial lengths

    for (int n = 0; n < (sizeof(weightedOutputs) / sizeof(int)); n++) {
      stimVals[i] = weightedOutputs[n];
      ISIDistribution[i] = random(isiMin, isiMax); //random isi distribution
      i++;
    }
  }
}//END POPULATE TRIALS



void bubbleUnsort(int *list, int elem){
  for (int a = elem - 1; a > 0; a--){
    int r = random(a + 1);
    //int r = rand_range(a+1);
    if (r != a){
      int temp = list[a];
      list[a] = list[r];
      list[r] = temp;
    }
  }
}
// generate a value between 0 <= x < n, thus there are n possible outputs
int rand_range(int n){
  int r, ul;
  ul = RAND_MAX - RAND_MAX % n;
  while ((r = random(RAND_MAX + 1)) >= ul);
  //r = random(ul);
  return r % n;
}
