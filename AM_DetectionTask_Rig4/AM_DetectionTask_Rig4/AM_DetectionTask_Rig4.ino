int state =1;
bool autoReward;
int outputLevels[12];
int outputWeights[12];
// state1 = autorreward (auto)
//state 2 = max stim only (S1)
// state 3 = add catch trials  (S2)
// state 4 = pyschometric curve (S3)
// state 5 = weighted psy curve (S4)


int magOnTime = 100;  //duration of magnet on time
int valveOpenTime = 20; //millis that the H20 valve is open
int lickResponseWindow = 1000;//amount of time mice have to response
int responseDelay = 500;  //time between stim onset and answer period
int preTrialNoLickTime = 1000;// no licks before trial or we tgrigger a false alarm
int timeOutDuration = 3000;  

//Specify pins
int lickportPin = 5;
int waterPin = 9;  
int magnetPin = 11;
int LEDpin = 3;
int triggerPin = 12;
int analogPin = 3;

//init vars
int thisTrialNumber = 0;
bool stimTime = false;
bool trialRunning = false;
bool lickOccured = false;
bool isResponseWindow = false;
bool initTrial = true;
bool trialRewarded = false;
bool resetTrial = false;
bool falseAlarm = false;
bool magnetOn = false;
bool waterPortOpen = false;
bool isRunning = false;
bool debug = false;

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
int resetTrialTime = 0;


void chooseParams() {
      if (state==1) {
          autoReward = true;
          outputLevels[0] = 255;
          outputWeights[0] = 1;
      }
      if (state==2) {
          autoReward = false;
          outputLevels[0] = 255;
          outputWeights[0] = 1;
      }
      
      //
      if (state==3) {
          autoReward = false;
          outputLevels[0] = 0;
          outputLevels[1] = 255;
          outputWeights[0] = 1;
          outputWeights[1] = 4;
      // 
      }
      //
      if (state==4) {
          autoReward = false;
          int theLevels[7] = {0,   43,   85,    128,    170,   213,  255};
          int theWeights[7] = {1, 1, 1, 1, 1, 1, 1};
          //for (index = 0; index < (sizeof(theWeights) / sizeof(int)); index++){
          //  outputLevels[index] = theLevels[index];
          //  outputWeights[index] = theWeights[index];
          //}
      }
      //
      if (state==5) {
        autoReward = false;
        int theLevels[7] = {0,   43,   85,    128,    170,   213,  255};
        int theWeights[7] = {1, 2, 3, 4, 3, 2, 1};
        //for (index = 0; index < (sizeof(theWeights) / sizeof(int)); index++){
        //  outputLevels[index] = theLevels[index];
        //  outputWeights[index] = theWeights[index];
        //}
      }
      //
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
  chooseParams();
  populateTrials();

  if (debug == false) {
     establishContact();
  }


  thisTrialNumber = 0;//cant figure out where or how this gets reset....but this fixes it
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.println("A");
    delay(300);
  }
}


// the loop function runs over and over again forever
void loop() {
    
   //FIRST, determine if the trial is running
   //read serial input = 1 turns on the system 0 turns it off
   if (Serial.available()) {
      val = Serial.read();
      if (val == '1')  {
        isRunning = true;
        //nextTrialStart = nextTrialStart + 5000;
      }
  
      if (val == '0') {
        isRunning = false;
        analogWrite(magnetPin, 0); // make sure mag and water are closed
        digitalWrite(waterPin, LOW);
      }
  }
  //end if we've exceeded the total number of rewards allowed
  if (cumRewards >= stopAfter_n_rewards) {
    isRunning = false;   
  }
  if (debug == true){ 
    isRunning = true;
  }

  //SECOND, if its running, do trial things.
  if (isRunning == true) {
    falseAlarm = false;  //reset this avr
    // DID A LICK OCCUR? Y/N
    lickOccured = false;
    if (digitalRead(lickportPin) == HIGH) {
      lickOccured = true;
    }

    //CLOSE WATER VALVE IF IT"S TIME   
    if (millis() >= valveCloseTime && waterPortOpen == true) {
      digitalWrite(waterPin, LOW); //close the water
      waterPortOpen = false;
      }


    //HANDLE ISI
    
    if (trialRunning == false) {
        //if we're in an inter trial interval, only two things can happen
        //1 - a false alarm
        if (nextTrialStart - (millis()) < preTrialNoLickTime && lickOccured == true) {
              nextTrialStart = nextTrialStart + timeOutDuration;
              falseAlarm = true;
        }
        
        //2 - trial begins
        if (millis()>=nextTrialStart) {
          // initialize trial
          thisTrialNumber=thisTrialNumber + 1;
          
          //SEND TRIGGER TO DAQ
          digitalWrite(triggerPin,HIGH); 

          analogWrite(analogPin,stimVals[thisTrialNumber+1]);  //SENT VOLTAGE TO DAQ

          //SET TIMER FOR STIMULUS ON
          stimStartTime = millis() + stimDelayStart; 
          stimEndTime = stimStartTime + magOnTime; 

          //SET TIMER FOR REWARD PERIOD START
          rewardPeriodStart = stimStartTime + responseDelay;
          
          //SET TIMER FOR REWARD PERIOD END
          rewardPeriodEnd = rewardPeriodStart + lickResponseWindow;
          resetTrialTime = rewardPeriodEnd + 100;
          // start the trial!
          trialRunning = true;
          trialStartTime = millis();
          stimTime = true;
        }
    }

    //HANDLE IN TRIAL
    //  we started a trial, and now after a brief delay to allow the DAQ to receive triggers, we turn on the stimulus
     if (millis()>= stimStartTime && trialRunning == true && stimTime == true) {
         // end triggers to daq
         digitalWrite(triggerPin,LOW);
         analogWrite(analogPin,0);  
         analogWrite(magnetPin,  stimVals[thisTrialNumber]);  // put voltage on the magnet
         magnetOn = true;
         stimTime = false;
     }

 //  turn off the magnet when it's time
 if (millis()>= stimEndTime && trialRunning == true && magnetOn == true) {
     // end triggers to daq
     analogWrite(magnetPin,  0);  // put voltage on the magnet
     magnetOn = false;
 }

 //  the reward period starts!
 if (millis()>= rewardPeriodStart && trialRunning == true && (millis()<rewardPeriodEnd))  {
    //  Serial.println(rewardPeriodEnd);

        isResponseWindow = true;        //set response window to 1
        
        if (autoReward == true && trialRewarded == false) {  //give water at same time as magnet
          digitalWrite(waterPin, HIGH); //open the water
          valveCloseTime = millis() + valveOpenTime; //mark time to close valve
          trialRewarded = true;
          cumRewards++;
          waterPortOpen = true;
        }


        if (autoReward == false && lickOccured == true && trialRewarded == false && stimVals[thisTrialNumber]>0) {  //give water at same time as magnet
          digitalWrite(waterPin, HIGH); //open the water
          valveCloseTime = millis() + valveOpenTime; //mark time to close valve
          trialRewarded = true;
          cumRewards++;
          waterPortOpen = true;
        }
 }


if ((millis()>=rewardPeriodEnd) && isResponseWindow == true && trialRunning == true) {
      //Serial.println("WHY");
      isResponseWindow = false;
   //  resetTrialTime = millis() + 100; 
      resetTrial = true;
      if (stimVals[thisTrialNumber] > 0 && trialRewarded == true) {
      analogWrite(analogPin,255);  // max volatge equals a hit

      }
  
      if (stimVals[thisTrialNumber] == 0 && trialRewarded == true) {
    //    Serial.println("bad catch");
      analogWrite(analogPin,0); // voltage = 0 indicated FAILED catch trial

      }


      if (stimVals[thisTrialNumber] == 0 && trialRewarded == false) {
      analogWrite(analogPin,191); //duty cycle of 75% indicates successful catch trial

      }



      if (stimVals[thisTrialNumber] > 0 && trialRewarded == false) {
     //  Serial.println("misssss");
      analogWrite(analogPin,64); // duty cycle of 25% indicates MISS

      }

}

if ((millis()>=resetTrialTime) && resetTrial == true && trialRunning == true) {

      analogWrite(analogPin,0);  //end transmission
      resetTrial = false;
      trialRunning = false;
      trialRewarded = false;
      nextTrialStart = millis() + ISIDistribution[thisTrialNumber]; //+1000;  // set time for next trial start
      Serial.println(nextTrialStart);
}



 
      
    


    //Serial Communicatiom
    if (debug == false) {
      Serial.print(millis() - trialStartTime);
      Serial.print(",");
      Serial.print(thisTrialNumber);
      Serial.print(",");
      Serial.print(trialRewarded);
      Serial.print(",");
      Serial.print(lickOccured);
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
      falseAlarm = false;
    }

  }

}

void populateTrials() {


  int arraySum;
  arraySum = 0;
  //Serial.print((sizeof(outputWeights) / sizeof(int)));
  int output_size = 0;
  for (int index = 0; index < (sizeof(outputWeights) / sizeof(int)); index++)
  {
    if (outputWeights[index] != 0){
      output_size++;
    }
  }
  for (int index = 0; index < output_size; index++)
  {
    arraySum += outputWeights[index];
  }


  //int outputLevels[7] = {0,   43,   85,    128,    170,   213,  255};
  //int outputWeights[7] = {1, 2, 3, 4, 3, 2, 1};

  //populate an array containing all the necessary duplicatses...
  int weightedOutputs[arraySum];
  int i = 0;
  for (int n = 0; n < output_size; n++) {
    for (int k = 0; (k < outputWeights[n]); k++) {

      weightedOutputs[i] = outputLevels[n];
      i++;
    }
  }

  //for (int i=0; i<(sizeof(weightedOutputs)/sizeof(int)); i++)
  //   {
  //     Serial.print("weightedOutputs[ ");
  //     Serial.print(i);      Serial.print(" ] = ");
  //     Serial.println(weightedOutputs[i]);
  //   }



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

//  for (int V=0; V<(14); V++)
//     {
//       Serial.print("array[ ");
//       Serial.print(V);     
//       Serial.print(" ] = ");
//       Serial.println(stimVals[V]);
//     }
//  

  // if (i<26) {
  //    Serial.print("stimvals of i = ");
  //    Serial.println(stimVals[i]);
  //    Serial.print("i = ");
  //    Serial.println(i);
  //    Serial.print("weightedOutputs of n = ");
  //    Serial.println(weightedOutputs[n]);
  //    Serial.print("n =  ");
  //    Serial.println(n);
  //    }



}//END POPULATE TRIALS



void bubbleUnsort(int *list, int elem)
{
  for (int a = elem - 1; a > 0; a--)
  {
    int r = random(a + 1);
    //int r = rand_range(a+1);
    if (r != a)
    {
      int temp = list[a];
      list[a] = list[r];
      list[r] = temp;
    }
  }
}
// generate a value between 0 <= x < n, thus there are n possible outputs
int rand_range(int n)
{
  int r, ul;
  ul = RAND_MAX - RAND_MAX % n;
  while ((r = random(RAND_MAX + 1)) >= ul);
  //r = random(ul);
  return r % n;
}
