#include <stdio.h>
#include <stdlib.h>


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

int trialNumber = 2000;
int state = 3;

int rand_range(int max){
    int x = rand() % (max + 1 - 0) + 0;
    return x;
}



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
          
          int add_to_index = (sizeof(theWeights_s1) / sizeof(int));
          for (int index = 0;
            index < (sizeof(theWeights_s2) / sizeof(int));
            index++){
                conditions[index+add_to_index][0] = size2;
                conditions[index+add_to_index][1] = theLevels_s2[index];
                conditionWeights[index+add_to_index] = theWeights_s2[index];
          }
          
          
}



void test(){
    int output_size = 0;
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
            // printf("(arraySum: %d)", arraySum);
          for (int k = 0; k < arraySum; k++) { // for all weights + conditions
              for (int optoW = 0; optoW < optoWeights[optoCond]; optoW++){
                  weightedOptoOutputs[wCondInd][0] = weightedOutputs[k][0];
                  weightedOptoOutputs[wCondInd][1] = weightedOutputs[k][1];
                  weightedOptoOutputs[wCondInd][2] = optoCond;
                  conditionIndexes[wCondInd] = wCondInd;
                   printf("%d & %d, ", weightedOutputs[k][1], optoCond);
                  
                  wCondInd++;
                  
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

  while (k < trialNumber) {
      
      
    for (int a = arrLen - 1; a > 0; a--){
        int r = rand_range(a);
        if (r != a){
          int temp = conditionIndexes[a];
         conditionIndexes[a] = conditionIndexes[r];
          conditionIndexes[r] = temp;
       }
    }
    for (int n = 0; n < (sizeof(conditionIndexes) / sizeof(int)); n++) {
      int condInd = conditionIndexes[n];
      stimVals[k] = weightedOptoOutputs[condInd][0];
      sizeVals[k] = weightedOptoOutputs[condInd][1];
      optoVals[k] = weightedOptoOutputs[condInd][2];
    
      
      printf("(%d, %d, %d)", stimVals[k],sizeVals[k],optoVals[k]);
      k++;
    }
  }
}
