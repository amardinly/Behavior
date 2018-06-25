public void updateBehaviorStats() {
  

 
        // just tally FAs since we can have many FAs per trial   
      if (falseAlarm>0) {
        falseAlarmTally++;
         //println("false alarm!!!!!!");
      }
  
  //if we move on to a next trial.....
      if (thisTrialNumber>previousTrialNumber) {
    
        
        if (hitTrial) {
        hitTally++;
        BinnedHitTally++;
       // println(BinnedHitTally);

        }
        else {
        missTally++;  
        BinnedMissTally++;
      //  println(BinnedMissTally);
        }
      
      hitTrial = false;
      previousTrialNumber = thisTrialNumber;
     // BinCrimenter++;
      }
    
      else
      
      {
      }
  
     //its a hit if the trial is ever rewarded 
     if (lickOccured>0 && isResponseWindow>0) { 
     hitTrial = true;  
     }
}