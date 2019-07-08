
#include <stdio.h>

int size1 = 20;
int size2 = 50;

int conditions[35][2];
int conditionWeights[35];

int optoWeights[2] = {3, 1};
int doOpto = 1; //MAKE THIS BOOL FOR ARDUINO

int sizeVals[3500];
int stimVals[3500];
int optoVals[3500];
int ISIdistribution[3500];

int trialNumber = 3000;
void chooseParams() {
      
          int theLevels_s1[6]={0,4,16,64,180,255};
          int theWeights_s1[6] = {1,1, 1, 1, 1, 1};
          
          int theLevels_s2[6]={0,2,6,16,32,255};
          int theWeights_s2[6] = {1,1, 1, 1, 1, 1};
          
          for (int index = 0; index < (sizeof(theWeights_s1) / sizeof(int)); index++){
            conditions[index][0] = size1;
            conditions[index][1] = theLevels_s1[index];
            conditionWeights[index] = theWeights_s1[index];
          }
          
          
          for (int index = (sizeof(theWeights_s1) / sizeof(int));
            index < (sizeof(theWeights_s2) / sizeof(int)) + (sizeof(theWeights_s1) / sizeof(int));
            index++){
                conditions[index][0] = size2;
                conditions[index][1] = theLevels_s2[index];
                conditionWeights[index] = theWeights_s2[index];
          }
          
}

int get_n_conditions(){
    int output_size = 0;
    for (int index = 0; index < (sizeof(conditionWeights) / sizeof(int)); index++){
    if (conditionWeights[index] != 0){
      output_size++;
    }
  }
  return output_size;
}

void bubbleUnsort(int *list, int elem){
  for (int a = elem - 1; a > 0; a--){
    int r = random(a+1);
    if (r != a){
      int temp = list[a];
      list[a] = list[r];
      list[r] = temp;
    }
  }
}


void populateTrials() {
   //the number of weights actually being used
  int output_size = get_n_conditions();
  //the total size of all weights added together
  int arraySum = 0;
  for (int index = 0; index < output_size; index++){
    arraySum += conditionWeights[index];
  }
  //populate an array containing all the necessary duplicatses...
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
      int arraySumTwo = optoWeights[0]*arraySum + optoWeights[1]*arraySum;
  }else{
      arraySumTwo = arraySum*2;
  }
  
  int weightedOptoOutputs[arraySumTwo][3];
  int conditionIndexes[arraySumTwo];
  
  if (doOpto==1){
      // then we'll duplicate that whole array, and give the firs thalf non opto weights
      int i=0;
      for (int n=0; n < 2; n++){
          for (int k = 0; k < arraySum; k++){
              for (int l=0; l < optoWeights[n]; l++){
                  weightedOptoOutputs[i][0] = weightedOutputs[i][0];
                  weightedOptoOutputs[i][1] = weightedOutputs[i][1];
                  weightedOptoOutputs[i][2] = n;
                  conditionIndexes[i] = i;
                  i++;
              }
            }
          }
  }
  else{
      //just duplicate it for randomizing purposes I guess
      int i=0;
      for (int n=0; n < 2; n++){
          weightedOptoOutputs[i][0] = weightedOutputs[i][0];
          weightedOptoOutputs[i][1] = weightedOutputs[i][1];
          weightedOptoOutputs[i][2] = 0;
          conditionIndexes[i] = i;
          i++;
      }
  }  
  


    
  int k = 0;
  int arrLen = sizeof(conditionIndexes) / sizeof(int);
  int rand_n;
  while (k < trialNumber) {
    bubbleUnsort(conditionIndexes, arrLen);       //randomize the weighted trial lengths

    for (int n = 0; n < (sizeof(conditionIndexes) / sizeof(int)); n++) {
      int condInd = conditionIndexes[n];
      stimVals[k] = weightedOptoOutputs[condInd][0];
      sizeVals[k] = weightedOptoOutputs[condInd][1];
      optoVals[k] = weightedOptoOutputs[condInd][2];
      
      k++;
    }
  }
}//END POPULATE TRIALS



void main()
{
    chooseParams();
    populateTrials();
    printf("its %d", optoVals[1]);
}
