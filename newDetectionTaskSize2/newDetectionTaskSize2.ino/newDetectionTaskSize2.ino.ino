#include <math.h>    // (no semicolon)
// state1 = autorreward (auto)
// state2 = add catch trials  (S2)
// state3 = pyschometric curve (S3)
// state4 = weighted psy curve (S4)
bool Rig = false;
bool synch = false;
bool visual = true;
bool do_timeout = true;
bool long_opto = false;
bool pre_opto = false;
bool random_opto = false;//how random opto works: it turns on between 100 and 2500 milliseconds before the visual stim. if a timeout happens, it is turned off, and a random opto is rerolled

int randomOptoMin = 300;
int randomOptoMax = 3000;
//int randomOptoMin = 100;
//int randomOptoMax = 300;

bool enforce_delay= false;

//these variables are uedependent on state/set by processing

int state = 1;
bool autoReward;
bool doOpto = true;
bool doOpto2 = true;  // Added by DANIEL
int conditions[35][2];
int conditionWeights[35];
int black_level = 0;
int grate_size1 = 100;
int grate_size2 = 600;
bool altISI = true;
int valveOpenTime = 0;
 



//Init Exp Defaults
int isiMin = 3000;//as in petersen paper orinal 3000 
int isiMax = 9000;

int trialNumber = 1000;  // um trials to allow
int trialStartTime = 2000;
int ISIDistribution[1050];  ///pad extra to prevent errors
int stimVals[1050];
int sizeVals[1050];
int optoVals[1050];
int stimDelayStart = 60;  // send a trigger to the DAQ 50 ms before stimulus
int magOnTime = 600;  //duration of magnet on time
 //millis that the H20 valve is open
int lickResponseWindow = 0;//amount of time mice have to response
int autoRewardDelay = 900;


//int responseDelay = 500;  //time btween stim offset and answer period
int responseDelay = 0;

int preTrialNoLickTime = 2000;// no licks before trial or we trigger a false alarm
int timeOutDurationMin = 5000;
int timeOutDurationMax = 9000;  
int timeOutSignalTime = 1000;
int timeOutToneTime = 1000;
int optoWeights[3] = {2,1,0};// 33% intermittent
//int optoWeights[3] = {1,1,1};// 2 LED intermittent

//int optoWeights[2] = {1,2};  // 66% intermittent
//int optoWeights[2] = {0,3}; //100% intermittent


//Specify pins
int lickportPin = 5;
int LEDPin = 2;
int LEDPin2 = 6; //Added by Daniel
int waterPin = 9;  
int magnetPin = 11;
int triggerPin = 12;
int analogPin = 3;
int readyToGoPin = 4;
int digOutPin = 7;
int stimIndicatorPin = 13;
int tonePin = 8;



//set the visual pins
int piOnPin = 33; //tell pi to turn stim on
int piInitPin = 34; //tell pi to turn stim off
int piReceivePin = 35; //tell pi to receive next trial stim info
const byte numPins = 8;
byte pins[] = {36, 37, 38, 39, 40, 41, 42, 43}; //pins for writing binary info
int piFAPin = 44;


//init vars altered during trials
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

String readString;

int valveCloseTime = 0;  
int nextTrialStart = 5000;  //5 sec baseline before we start stuff
int turnOffStim = 0;
int turnOffResponseWindow = 0;
int cumRewards = 0;
bool init_pi = false;

int stimStartTime = 0;
int stimEndTime = 0;
int rewardPeriodStart =0;
int rewardPeriodEnd = 0;
int lickCounter = 0;
int pulsesSent = 0;
int nextPulseTime = 0;
int nextStimIdx = 0;
int timeOutEnd = 0;
int gracePeriodEnd = 0;
bool timeOutSignalOn = false;
bool delayFailed= false;
int timeOutSignalEnd = 0;

int isOpto = 0; // 5/18/21 change to int to take multiple values
bool ledOn = false; //as of 4/6 actually using this distinguisher
bool ledOn2 = false;

int optoStartTime = 0;
bool donePulsing = false;
char val;  //data received from serial port


// the setup function runs once when you press reset or power the board or start a serial connection

void setup(){
  randomSeed(analogRead(0)); //make the random generator more random
  setupPins();
  Serial.begin(9600);
  if (debug == false) {
     establishContact();
  } 
  chooseParams();  populateTrials();
  thisTrialNumber = 0;//cant figure out where or how this gets reset....but this fixes it
  
}

int genISI(int mint, int maxt){
  // 7/9 switched back to uniform while awaiting new plan
  //double min = double(mint);
  //double max = double(maxt);
  //double q = 2/(max-min);
  //double R = double(random(1,1001))/double(1000); //won't generate doubles so gotta do it this way
  //double isi = -1/q*log(exp(-q*min)- (exp(-q*min)-exp(-q*max))*R);
  int isi = random(mint,maxt);
  return int(isi);
}

int getRandOptoStart(){
  int optoStartTime = nextTrialStart - random(randomOptoMin, randomOptoMax);
  return optoStartTime;
}

void turnRandOptoOnOnTime(){
  //checks if the time is right to turn on random opto
  isOpto = optoVals[thisTrialNumber+1];
  
  handleLEDOnOff();
}

bool setIsOpto(){
  //7/29 changed 
  isOpto = optoVals[thisTrialNumber];
  handleLEDOnOff();
}

bool setIsLongOpto(){
  isOpto = optoVals[thisTrialNumber+1];
  handleLEDOnOff();
}

void handleLEDOnOff(){
  if (isOpto==0){ 
    turnLEDOff();
    turnLED2Off(); 
  } else if (isOpto==1) {
    turnLEDOn();
    turnLED2Off(); 
  } else if (isOpto==2){
    turnLEDOff();
    turnLED2On(); 
  }
}



void prepTrial(){
      if (visual==true){
        sendPiNumber(sizeVals[thisTrialNumber+1]);
        delay(50); endSendPiNumber(); delay(50);
        sendPiNumber(stimVals[thisTrialNumber+1]);
      }
}



void startTrial(){
      thisTrialNumber=thisTrialNumber + 1;

      if (Rig == true && synch == true) {
        daqReady = false;
        //SEND TRIGGER TO DAQ
        digitalWrite(triggerPin,HIGH); 
        getNextStimIdx(); //will change a global correctly, is for daq comm
      }   
      Serial.print('this trial is');
      Serial.println(optoVals[thisTrialNumber]==1);
      //SET TIMER FOR STIMULUS
      stimStartTime = millis() + stimDelayStart; 
      stimEndTime = stimStartTime + magOnTime; 
      //TIMER FOR PULSING
      nextPulseTime = millis() + stimDelayStart;
      //SET TIMER FOR REWARD PERIOD START
      rewardPeriodStart = stimEndTime + responseDelay;
      //SET TIMER FOR REWARD PERIOD END
      rewardPeriodEnd = rewardPeriodStart + lickResponseWindow;
      trialStartTime = millis();
      
      endSendPiNumber(); //cease trial start signals      

}


void resetTrial(){
  digitalWrite(triggerPin,LOW); //end trigger, ONLY MATTERS FOR RIG
  trialRewarded = false;
  catchFA = false;
  pulsesSent = 0;
  nextStimIdx = 0;
  donePulsing = false;
  delayFailed= false;
  
  nextTrialStart = millis() + random(isiMin,isiMax); //+1000;  // set time for next trial start
  optoStartTime = getRandOptoStart(); //only used if random opto
  
  if (altISI==true){
    nextTrialStart = millis() + genISI(isiMin, isiMax);
  }

  gracePeriodEnd = millis() + timeOutSignalTime;
  //7/29 changed setIsOpto();
  if (long_opto==true){
    setIsLongOpto();
  }
}





//--------------------------------------------------///

//--------------------------------------------------///

// the loop function runs over and over again forever

void loop() {

  checkSerial();

   

  //if its running, do trial things.

  if (isRunning == true) {

      prepTrial(); //send values to pi

        

      //first, begin in the ISI stage, hold in this while loop

      while ((millis() < nextTrialStart || daqReady==false) && isRunning == true){
        falseAlarm = false;  //reset this 
        lickOccured = isLicking();

        //RIG ONLY: if daq is not yet ready, check if ready
        if (daqReady == false){daqReady = isDaqReady();}

           
        //check if a false alarm occured, act accordingly

        if (altISI==false){
          if (nextTrialStart - (millis()) < preTrialNoLickTime && lickOccured == true) {
                  nextTrialStart = nextTrialStart + random(timeOutDurationMin,timeOutDurationMax);
                  optoStartTime = getRandOptoStart();
                  falseAlarm = true;
                  if (random_opto==true){
                    turnLEDOff();
                  }
                  turnTimeOutSignalOn();
          }
        } else{
          //grace period for time out handled by the time out signal
          if (lickOccured == true && timeOutSignalOn == false && millis()>gracePeriodEnd){
            //setIsOpto(); //randomly select opto or not and turn LED on or off
            nextTrialStart = millis() + genISI(isiMin, isiMax); //could also be TO min + max
            falseAlarm = true;
            turnTimeOutSignalOn();

          }

        }

        

        turnTimeOutSignalOffOnTime();
        if (random_opto==true){
          turnRandOptoOnOnTime();
        }
        //talk to serial at the end of each loop of while, and check on serial too
        sendSerial();
        checkSerial();
      }

      if (isRunning==false){
        return; // exit loop to hold in checkSerial
      }

      // just in case, shutoff timeout signals
      digitalWrite(piFAPin, LOW);  timeOutSignalOn = false;



      startTrial(); // initialize trial

      if (pre_opto==true && long_opto==false && random_opto==false){
        setIsOpto(); //3/21
      }

      while (millis()<=stimStartTime){ //wait till stim on
        sendSerial();
      }

      if (long_opto==false && pre_opto==false && random_opto==false){
        setIsOpto(); // 7/29
      }
      
      turnStimOn(); //stim goes on

      

      while (millis() < stimEndTime) { //during stim presentation
        sendSerial();
        lickOccured = isLicking();
        if ((enforce_delay==true) && (lickOccured ==true)){
          delayFailed = true;
          turnTimeOutSignalOn();
          falseAlarm=true; //use this to indicate punished early licking for now
          break;
        }
        sendSerial();
        falseAlarm=false; 
        //if (Rig==true){doPulsingStimIdx();}
      }

      turnStimOff(); //stim goes off

      while ((millis() < rewardPeriodStart) && (delayFailed==false)){ //then wait for the reward period
        sendSerial();
        lickOccured = isLicking();
        //Serial.println(delayFailed);
        if ((enforce_delay ==true) && (lickOccured==true)){
          delayFailed = true;
          turnTimeOutSignalOn();
          break;
        }
      }
      //if (Rig==true){doPulsingStimIdx();
 
    
      //begin + handle reward period
      isResponseWindow = true;
      
      
      // For delay task comment from here to...
      
    if ((autoReward == true)&& (delayFailed==false)){ //if autoreward, begin giving water
        turnWaterOn();
      }
      // Up to here

      while ((millis()>= rewardPeriodStart) && (millis()<rewardPeriodEnd)&& (delayFailed==false))  {
            if (isLicking()==true && autoReward == false && trialRewarded == false){
              if (stimVals[thisTrialNumber]>0){
                turnWaterOn();
              } else {
                catchFA = true;
                turnTimeOutSignalOn();
              }
            }


      if ((autoReward == true)&& (delayFailed==false)&& (millis()>= rewardPeriodStart+autoRewardDelay) && (trialRewarded==false)){ //if autoreward, begin giving water
        turnWaterOn();
      }
          //if (Rig==true){doPulsingStimIdx();}
          turnWaterOffOnTime();
          turnTimeOutSignalOffOnTime();
          sendSerial();
      }

      //just in case, turn off water
      digitalWrite(waterPin, LOW); waterPortOpen = false;
      isResponseWindow = false;
      sendSerial();
      //7/29 CHANGED
      turnLEDOff();
      turnLED2Off(); // Added by DANIEL 

        

      //make sure we finished sending mag stim idx pulse
      //if (Rig == true){ while (donePulsing==false){doPulsingStimIdx(); sendBehaviorOutcome();
       

    

      // give a time out for false alarm licking after the response window
      if ((catchFA==true) || (delayFailed==true)){
        timeOutEnd = rewardPeriodEnd + random(timeOutDurationMin,timeOutDurationMax);
        while (millis()<=timeOutEnd){
          turnTimeOutSignalOffOnTime();
          checkSerial();
          sendSerial();
        }
      }

        

      // just in case
      digitalWrite(piFAPin, LOW);
      timeOutSignalOn = false;
      

      resetTrial(); 
      sendSerial();

  }

}
