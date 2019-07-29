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
        autoReward=true;
          int theLevels_s1[1]={250};
          int theWeights_s1[1] = {1};       
          int theLevels_s2[1]={250};
          int theWeights_s2[1] = {1};
          
          for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++){
            conditions[index][0] = grate_size1;
            conditions[index][1] = theLevels_s1[index];
            conditionWeights[index] = theWeights_s1[index];
          }
          
          int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
          for (int index = 0;
            index < (sizeof(theWeights_s2) / sizeof(int));
            index++){
                conditions[index+add_to_index][0] = grate_size2;
                conditions[index+add_to_index][1] = theLevels_s2[index];
                conditionWeights[index+add_to_index] = theWeights_s2[index];
          }
      }
      if (state==2) {
          autoReward = false;
         int theLevels_s1[2]={0,250};
          int theWeights_s1[2] = {1,4};       
          int theLevels_s2[2]={0,250};
          int theWeights_s2[2] = {1,4};
          
          for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++){
            conditions[index][0] = grate_size1;
            conditions[index][1] = theLevels_s1[index];
            conditionWeights[index] = theWeights_s1[index];
          }
          
          int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
          for (int index = 0;
            index < (sizeof(theWeights_s2) / sizeof(int));
            index++){
                conditions[index+add_to_index][0] = grate_size2;
                conditions[index+add_to_index][1] = theLevels_s2[index];
                conditionWeights[index+add_to_index] = theWeights_s2[index];
          }
      }
      if (state==3) {
          autoReward = false;
          
          int theLevels_s1[6]={13,51,190,204,220,250}; // easy 
          //int theLevels_s1[6]={10,35,51,130,204,250}; //hard for 56.2
          int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
          int theLevels_s2[6]={0,3,13,64,100,170}; //easy 
          int theWeights_s2[6] = {1, 1, 1, 1, 1,1}; //easy
          //int theLevels_s2[7]={0,4,10,25,50,100,192}; //hard for 56.2
          //int theWeights_s2[7] = {1, 1, 1, 1, 1,1,1};
         
          for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++){
            conditions[index][0] = grate_size1;
            conditions[index][1] = theLevels_s1[index];
            conditionWeights[index] = theWeights_s1[index];
          }
          
          int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
          for (int index = 0;
            index < (sizeof(theWeights_s2) / sizeof(int));
            index++){
                conditions[index+add_to_index][0] = grate_size2;
                conditions[index+add_to_index][1] = theLevels_s2[index];
                conditionWeights[index+add_to_index] = theWeights_s2[index];
          }
          
      }
}


void populateTrials() {int output_size = 0;
    for (int index = 0; index < (sizeof(conditionWeights) / sizeof(int)); index++){
    if (conditionWeights[index] != 0){
      output_size++;
    }
   }

  int arraySum = 0;
  for (int index = 0; index < output_size; index++){
    arraySum += conditionWeights[index];
  }
  
  int weightedOutputs[arraySum][2];
  int i = 0;
  //for each unique contrast and associated weight
  for (int n = 0; n < output_size; n++) {
    //duplicate it weights number of times
    for (int k = 0; (k < conditionWeights[n]); k++) {
      weightedOutputs[i][0] = conditions[n][0];
      weightedOutputs[i][1] = conditions[n][1];
      i++;
    }
  }
  int arraySumTwo;
  if (doOpto==1){
      arraySumTwo = optoWeights[0]*arraySum + optoWeights[1]*arraySum;
  }else{
      arraySumTwo = arraySum*2;
  }
  
  int weightedOptoOutputs[arraySumTwo][3];
  int conditionIndexes[arraySumTwo];
  
  if (doOpto==1){
      // then we'll duplicate that whole array, and give the firs thalf non opto weights
      int wCondInd=0;
      for (int optoCond=0; optoCond < 2; optoCond++){ // each opto condition
          for (int k = 0; k < arraySum; k++) { // for all weights + conditions
              for (int optoW = 0; optoW < optoWeights[optoCond]; optoW++){
                  weightedOptoOutputs[wCondInd][0] = weightedOutputs[k][0];
                  weightedOptoOutputs[wCondInd][1] = weightedOutputs[k][1];
                  weightedOptoOutputs[wCondInd][2] = optoCond;
                  conditionIndexes[wCondInd] = wCondInd;
                  
                  wCondInd++;
              }
            }
          }
  }
  else{
      //just duplicate it for randomizing purposes I guess
      int i=0;
      for (int n=0; n < 2; n++){
        for (int k = 0; k < arraySum; k++) { // for all weights + conditions
          weightedOptoOutputs[i][0] = weightedOutputs[k][0];
          weightedOptoOutputs[i][1] = weightedOutputs[k][1];
          weightedOptoOutputs[i][2] = 0;
          conditionIndexes[i] = i;
          i++;
        }
      }
  }
  
  int k = 0;
  int arrLen = sizeof(conditionIndexes) / sizeof(int);

  while (k < trialNumber) {
    for (int a = arrLen - 1; a > 0; a--){
        int r = random(0,a+1);
        if (r != a){
          int temp = conditionIndexes[a];
         conditionIndexes[a] = conditionIndexes[r];
          conditionIndexes[r] = temp;
       }
    }
    for (int n = 0; n < (sizeof(conditionIndexes) / sizeof(int)); n++) {
      int condInd = conditionIndexes[n];
      sizeVals[k] = weightedOptoOutputs[condInd][0];
      stimVals[k] = weightedOptoOutputs[condInd][1];
      optoVals[k] = weightedOptoOutputs[condInd][2];
      
      k++;
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
