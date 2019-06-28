void setupPins(){
  pinMode(magnetPin, OUTPUT);
  pinMode(waterPin, OUTPUT);
  pinMode(LEDPin, OUTPUT);
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
  pinMode(piFAPin, OUTPUT);
  digitalWrite(piInitPin, LOW);
  digitalWrite(piReceivePin, LOW);
  digitalWrite(piFAPin, LOW);
  for (int i=0; i<numPins; i++){
    pinMode(pins[i], OUTPUT);
    digitalWrite(pins[i], LOW);
  }
}

void chooseParams() {
      // set autoreward and contrast levels based on state chosen
      if (state==1) {
          autoReward = true;
          outputLevels[0] = 250;
          outputWeights[0] = 1;
      }
      if (state==2) {
          autoReward = false;
          outputLevels[0] = 0;
          outputLevels[1] = 250;
          outputWeights[0] = 1;
          outputWeights[1] = 4;
      }
      if (state==3) {
          autoReward = false;
           int theLevels[8]={0,4,16,64,128,180,220,255};
          int theWeights[8] = {1,1, 1, 1, 1, 1, 1,1};
          for (int index = 0; index < (sizeof(theWeights) / sizeof(int)); index++){
            outputLevels[index] = theLevels[index];
            outputWeights[index] = theWeights[index];
          }
      }
}


void populateTrials() {
  int arraySum;
  arraySum = 0;
  //the number of weights actually being used
  int output_size = 0;
  for (int index = 0; index < (sizeof(outputWeights) / sizeof(int)); index++){
    if (outputWeights[index] != 0){
      output_size++;
    }
  }
  //the total size of all weights added together
  for (int index = 0; index < output_size; index++){
    arraySum += outputWeights[index];
  }
  //populate an array containing all the necessary duplicatses...
  int weightedOutputs[arraySum];
  int i = 0;
  //for each unique contrast and associated weight
  for (int n = 0; n < output_size; n++) {
    //duplicate it weights number of times
    for (int k = 0; (k < outputWeights[n]); k++) {
      weightedOutputs[i] = outputLevels[n];
      i++;
    }
  }

  i = 0;
  int arrLen = sizeof(weightedOutputs) / sizeof(int);
  int rand_n;
  while (i < trialNumber) {
    bubbleUnsort(weightedOutputs, arrLen);       //randomize the weighted trial lengths

    for (int n = 0; n < (sizeof(weightedOutputs) / sizeof(int)); n++) {
      stimVals[i] = weightedOutputs[n];
      ISIDistribution[i] = random(isiMin, isiMax); //random isi distribution
      rand_n = random(1,100);
      if (rand_n>50){
            sizeVals[i] = grate_size1;
      } else{
            sizeVals[i] = grate_size2;
      }
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
