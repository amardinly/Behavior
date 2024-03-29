void setupPins() {
  pinMode(magnetPin, OUTPUT);
  pinMode(waterPin, OUTPUT);
  pinMode(LEDPin, OUTPUT);
  pinMode(LEDPin2, OUTPUT);

  pinMode(lickportPin, INPUT);  // OR INTERRUPT
  analogWrite(magnetPin, 0); // make sure mag and water are closed
  digitalWrite(waterPin, LOW);
  pinMode(triggerPin, OUTPUT);
  pinMode(analogPin, OUTPUT);
  pinMode(readyToGoPin, INPUT);
  pinMode(digOutPin, OUTPUT);
  pinMode(stimIndicatorPin, OUTPUT);
  pinMode(piOnPin, OUTPUT);
  pinMode(piInitPin, OUTPUT);
  pinMode(piReceivePin, OUTPUT);
  pinMode(piFAPin, OUTPUT);
  digitalWrite(piInitPin, LOW);
  digitalWrite(piReceivePin, LOW);
  digitalWrite(piFAPin, LOW);
  for (int i = 0; i < numPins; i++) {
    pinMode(pins[i], OUTPUT);
    digitalWrite(pins[i], LOW);
  }
}

void chooseParams() {

  // set autoreward and contrast levels based on state chosen
  if (state == 1) {
    autoReward = true;
    int theLevels_s1[1] = {250};
    int theWeights_s1[1] = {1};
    int theLevels_s2[1] = {250};
    int theWeights_s2[1] = {1};

    for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++) {
      conditions[index][0] = grate_size1;
      conditions[index][1] = theLevels_s1[index];
      conditionWeights[index] = theWeights_s1[index];
    }

    int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
    for (int index = 0;
         index < (sizeof(theWeights_s2) / sizeof(int));
         index++) {
      conditions[index + add_to_index][0] = grate_size2;
      conditions[index + add_to_index][1] = theLevels_s2[index];
      conditionWeights[index + add_to_index] = theWeights_s2[index];
    }
  }
  if (state == 2) {
    autoReward = false;
    int theLevels_s1[2] = {0, 250};
    int theWeights_s1[2] = {1, 4};
    int theLevels_s2[2] = {0, 250};
    int theWeights_s2[2] = {1, 4};

    for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++) {
      conditions[index][0] = grate_size1;
      conditions[index][1] = theLevels_s1[index];
      conditionWeights[index] = theWeights_s1[index];
    }

    int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
    for (int index = 0;
         index < (sizeof(theWeights_s2) / sizeof(int));
         index++) {
      conditions[index + add_to_index][0] = grate_size2;
      conditions[index + add_to_index][1] = theLevels_s2[index];
      conditionWeights[index + add_to_index] = theWeights_s2[index];
    }
  }
  if (state == 3) {
    autoReward = false;


    int theLevels_s1[7] = {13, 51, 64, 190, 204, 220, 250}; // easy
    int theWeights_s1[7] = {1, 1, 1, 1, 1, 1, 1};
    int theLevels_s2[6] = {0, 3, 13, 64, 100, 170}; //easy
    int theWeights_s2[6] = {1, 1, 1, 1, 1, 1}; //easy

    for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++) {
      conditions[index][0] = grate_size1;
      conditions[index][1] = theLevels_s1[index];
      conditionWeights[index] = theWeights_s1[index];
    }

    int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
    for (int index = 0;
         index < (sizeof(theWeights_s2) / sizeof(int));
         index++) {
      conditions[index + add_to_index][0] = grate_size2;
      conditions[index + add_to_index][1] = theLevels_s2[index];
      conditionWeights[index + add_to_index] = theWeights_s2[index];
    }
  }
  if (state == 4) {
    autoReward = false;
    timeOutDurationMin = 5000;
    timeOutDurationMax = 9000;
    isiMin = 3000;
    
    isiMax = 9000;
    

    
   

    int theLevels_s1[6]={3,5,8,14,90,220}; //  Ai203
    int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    int theLevels_s2[1]={0}; //
    int theWeights_s2[1] = {2}; //


  


    //int theLevels_s1[6]={3,8,14,50,90,220}; // INITIAL Intensities PVs size 50
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //


    //int theLevels_s1[6]={6,19,32,77,128,220}; // INITIAL Intensities PVs size 25
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
   // int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //
    
    
    
    //int theLevels_s1[6]={2,7,11,27,45,220}; // INITIAL Intensities PVs size 90
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //


    //int theLevels_s1[6]={6,10,19,77,128,220}; // EMX Mice size 25
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //


    //int theLevels_s1[6]={3,8,14,50,90,220}; //  
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //



    

    //int theLevels_s1[6]= {3,10,16,50,100,250}; // Controls
    //int theWeights_s1[6] = {1,1, 1, 1, 1,1};// Size 1:15
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //

    
    //int theLevels_s1[6]= {3,16,25,50,100,250}; // Controls
    //int theWeights_s1[6] = {1,1, 1, 1, 1,1};// Size 1:20
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //

    //int theLevels_s1[6]= {3,8,10,18,100,250}; // Controls
    //int theWeights_s1[6] = {1,1, 1, 1, 1,1};// Size 1:25
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //
    





    //int theLevels_s1[6]= {3,8,14,20,100,250}; // Controls
    //int theWeights_s1[6] = {1,1, 1, 1, 1,1};// Size 1:30
    ///int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //


    //int theLevels_s1[6]= {3,8,12,15,100,250}; // Controls
    //int theWeights_s1[6] = {1,1, 1, 1, 1,1};// Size 1:35
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //


    //int theLevels_s1[6]={2,4,9,15,100,220}; // Controls SIZE 50 
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //


    //int theLevels_s1[6]={2,4,8,11,70,220}; // Controls SIZE 70 
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //
    


    //int theLevels_s1[6]={2,4,6,10,50,150}; // Controls SIZE 90 
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //
    
    




    for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++) {
      conditions[index][0] = grate_size1;
      conditions[index][1] = theLevels_s1[index];
      conditionWeights[index] = theWeights_s1[index];
    }

    int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
    for (int index = 0;
         index < (sizeof(theWeights_s2) / sizeof(int));
         index++) {
      conditions[index + add_to_index][0] = grate_size2;
      conditions[index + add_to_index][1] = theLevels_s2[index];
      conditionWeights[index + add_to_index] = theWeights_s2[index];
    }

  }

  if (state == 5) {
    autoReward = false;
    timeOutDurationMin = 2000;
    timeOutDurationMax = 4000;
    isiMin = 1000;
    isiMax = 4000;
    lickResponseWindow = 500;







    int theLevels_s1[6]={3,18,30,100,190,220}; // INITIAL Intensities for 123.4 FOR SIZE 50
    int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    int theLevels_s2[1]={0}; //
    int theWeights_s2[1] = {1}; //


    //int theLevels_s1[6] = {5, 10, 15, 50, 190, 250}; // Halo 77.4 2B
    //int theWeights_s1[6] = {1, 1, 1, 1, 1, 1};
    //int theLevels_s2[1] = {0}; //
    //int theWeights_s2[1] = {5}; //



    //int theLevels_s1[6]={5,13,25,190, 220, 250}; // Halo 87.1  2C
    //int theWeights_s1[6] = {1,1, 1, 1, 1, 1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {5}; //

    //int theLevels_s1[6]={5,10,15,50,190,250}; // Halo 77.1 2C
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {5}; //

    //int theLevels_s1[6]={5,10,18,50,190, 250}; // Halo 87.3  2B
    //int theWeights_s1[6] = {1, 1, 1, 1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {5}; //



    //int theLevels_s1[7]={5,10,18, 25, 190,204, 250}; // Halo 87.2  2A
    //int theWeights_s1[7] = {1,1, 1, 1,  1, 1,1};
    //int theLevels_s2[1]={0}; //
    //int theWeights_s2[1] = {2}; //



    for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++) {
      conditions[index][0] = grate_size1;
      conditions[index][1] = theLevels_s1[index];
      conditionWeights[index] = theWeights_s1[index];
    }

    int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
    for (int index = 0;
         index < (sizeof(theWeights_s2) / sizeof(int));
         index++) {
      conditions[index + add_to_index][0] = grate_size2;
      conditions[index + add_to_index][1] = theLevels_s2[index];
      conditionWeights[index + add_to_index] = theWeights_s2[index];
    }

  }
}


void populateTrials() {
  int output_size = 0;
  for (int index = 0; index < (sizeof(conditionWeights) / sizeof(int)); index++) {
    if (conditionWeights[index] != 0) {
      output_size++;
    }
  }

  int arraySum = 0;
  for (int index = 0; index < output_size; index++) {
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
  //changes to make opto weights be variable size
  int lenOptoW = sizeof(optoWeights) / sizeof(int);
  if (doOpto == 1) {
    arraySumTwo = 0;
    for (int n = 0; n < lenOptoW; n++) {
      arraySumTwo += optoWeights[n] * arraySum;
    }
  } else {
    arraySumTwo = arraySum * 2;
  }

  int weightedOptoOutputs[arraySumTwo][3];
  int conditionIndexes[arraySumTwo];

  if (doOpto == 1) {
    // then we'll duplicate that whole array, and give the firs thalf non opto weights
    int wCondInd = 0;
    for (int optoCond = 0; optoCond < lenOptoW; optoCond++) { // each opto condition
      for (int k = 0; k < arraySum; k++) { // for all weights + conditions
        for (int optoW = 0; optoW < optoWeights[optoCond]; optoW++) {
          weightedOptoOutputs[wCondInd][0] = weightedOutputs[k][0];
          weightedOptoOutputs[wCondInd][1] = weightedOutputs[k][1];
          weightedOptoOutputs[wCondInd][2] = optoCond;
          conditionIndexes[wCondInd] = wCondInd;

          wCondInd++;
        }
      }
    }
  }
  else {
    //just duplicate it for randomizing purposes I guess
    int i = 0;
    for (int n = 0; n < 2; n++) {
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
    for (int a = arrLen - 1; a > 0; a--) {
      int r = random(0, a + 1);
      if (r != a) {
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



void bubbleUnsort(int *list, int elem) {
  for (int a = elem - 1; a > 0; a--) {
    int r = random(a + 1);
    //int r = rand_range(a+1);
    if (r != a) {
      int temp = list[a];
      list[a] = list[r];
      list[r] = temp;
    }
  }
}

// generate a value between 0 <= x < n, thus there are n possible outputs
int rand_range(int n) {
  int r, ul;
  ul = RAND_MAX - RAND_MAX % n;
  while ((r = random(RAND_MAX + 1)) >= ul);
  //r = random(ul);
  return r % n;
}
