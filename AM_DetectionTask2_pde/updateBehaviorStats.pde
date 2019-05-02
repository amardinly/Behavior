public void updateBehaviorStats() {
  

 
        // just tally FAs since we can have many FAs per trial   
      if (falseAlarm>0) {
        falseAlarmTally++;
         //println("false alarm!!!!!!");
      }
  
  //if we move on to a next trial.....
      if (thisTrialNumber>previousTrialNumber) {
    
        
        if (isCatchTrial) {
          if(licked) {
            faCatchTally ++;
          }
          else {
            crTally++;
          }
        }
        else{
          if(licked) {
          hitTally++;
          BinnedHitTally++;
         // println(BinnedHitTally);
  
          }
          else {
          missTally++;  
          BinnedMissTally++;
        //  println(BinnedMissTally);
          }
        }
      
      isCatchTrial = false;
      licked = false;
      previousTrialNumber = thisTrialNumber;
     // BinCrimenter++;
      }
    
      else
      
      {
      }
      
      lastStim = stimVoltage;
      if (stimVoltage == 0){
        isCatchTrial = true;
      }
     //
     if(lickOccured>0 && isResponseWindow>0) { 
       licked = true;  
     }
}