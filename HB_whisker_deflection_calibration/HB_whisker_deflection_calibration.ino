int state = 1;
// state1 = basic set of strengths, 5x per strength
bool Rig = true;
bool synch = false;


int outputLevels[20];
int outputWeights[20];



int magOnTime = 100;  //duration of magnet on time
int isi = 500;  //interstim interval

//Specify pins
int lickportPin = 5;
int waterPin = 9;  
int magnetPin = 11;
int LEDpin = 3;
int triggerPin = 12;
int analogPin = 3;
int readyToGoPin = 4;

//init vars
int thisTrialNumber = 0;
bool stimTime = false;
bool trialRunning = false;
bool initTrial = true;
bool resetTrial = false;
bool magnetOn = false;
bool isRunning = false;
bool debug = true;
bool daqReady = true;

int valveCloseTime = 0;  
int nextTrialStart = 5000;  //5 sec baseline before we start stuff
int turnOffStim = 0;
int turnOffResponseWindow = 0;
char val;  //data received from serial port


//Init Exp Defaults
const int trialNumber = 50;  // num trials to allow
int trialStartTime = 2000;
int stimVals[trialNumber];
int stimDelayStart = 50;  // send a trigger to the DAQ 50 ms before stimulus
int stimStartTime = 0;
int stimEndTime = 0;
int resetTrialTime = 0;


void chooseParams() {
      if (state==1) {
         int theLevels[10] = {0,3,5,10,21,30,43,85,128,255};
         int theWeights[10] = {1,1,1, 1, 1, 1, 1, 1, 1, 1};
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
  chooseParams();  populateTrials();


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
  
  if (debug == true){ 
    isRunning = true;
  }
  if (thisTrialNumber > trialNumber){
      isRunning=false;
  }
  

  //SECOND, if its running, do trial things.
  if (isRunning == true) {


   //check to see if its ok to move to next trial
   if (digitalRead(readyToGoPin)==HIGH && daqReady == false) {
    daqReady = true;
    // if we're just getting the ready signal, but the trial was gonna start in 500 ms
    // give matlab a little more time to get it right
    
    if (nextTrialStart<=millis()+500) {
      nextTrialStart = millis() + 500; 

     // Serial.println("time extended");
      
    }
   }
   

    //HANDLE ISI
    
    if (trialRunning == false) {
        //if its time to start the trial, start it
        if (millis()>=nextTrialStart && daqReady==true) {
          // initialize trial
          //TEMP - don't use daq ready signal?
          //if (Rig == true && synch == true) {
          //daqReady = false;
          //}
          
          thisTrialNumber=thisTrialNumber + 1;
          
          //SEND TRIGGER TO DAQ
          digitalWrite(triggerPin,HIGH); 

          analogWrite(analogPin,stimVals[thisTrialNumber-1]);  //SENT VOLTAGE TO DAQ of current trial

          //SET TIMER FOR STIMULUS ON
          stimStartTime = millis() + stimDelayStart; 
          stimEndTime = stimStartTime + magOnTime; 

          // start the trial!
          trialRunning = true;
          trialStartTime = millis();
          stimTime = true;
        }
    }

    //HANDLE IN TRIAL
    //  we started a trial, and now after a brief delay to allow the DAQ to receive triggers, we turn on the stimulus
     if (millis() >= stimStartTime && trialRunning == true && stimTime == true) {
         // end triggers to daq
         digitalWrite(triggerPin,LOW);
         analogWrite(analogPin,0);  
         analogWrite(magnetPin,  stimVals[thisTrialNumber-1]);  // put voltage on the magnet
         magnetOn = true;
         stimTime = false;
     }

 //  turn off the magnet and end the trail when it's time
 if (millis()>= stimEndTime && trialRunning == true && magnetOn == true) {
     // end triggers to daq
     analogWrite(magnetPin,  0);  // put voltage on the magnet
     magnetOn = false;
	trialRunning=false;
	nextTrialStart = millis()+isi;
 }

    //Serial Communicatiom
    
      Serial.print(millis() - trialStartTime);
      Serial.print(",");
      Serial.print(thisTrialNumber);
      //Serial.print(",");
      //Serial.print(trialRewarded);
      Serial.print(",");
      //Serial.print(lickOccured);
      //Serial.print(",");
      Serial.print(stimVals[thisTrialNumber-1]);
      //Serial.print(",");
      //Serial.print(isResponseWindow);
      Serial.print(",");
      Serial.print(magnetOn);
      //Serial.print(",");
      //Serial.print(waterPortOpen);
      //Serial.print(",");
      //Serial.println(falseAlarm);
      Serial.print("\n");
    

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
