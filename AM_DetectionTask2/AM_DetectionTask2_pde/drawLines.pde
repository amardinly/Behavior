public void drawLines() {

   //calculate the average
   // average = total/numReadings;

    // Shift array values
    for (int i = 0; i < mx.length-1; i ++ ) {
      // Shift all elements down one spot. 
      // xpos[0] = xpos[1], xpos[1] = xpos = [2], and so on. Stop at the second to last element.
      mx[i] = mx[i+1]; 
      //myLED[i] = myLED[i+1];
      //myTA[i] = myTA[i+1];
      //myLickL[i] = myLickL[i+1];
      myStimVal[i]=myStimVal[i+1];
     // println(mx[i]);
      myLick[i] = myLick[i+1];
      myRewardPeriod[i] = myRewardPeriod[i+1];
      myReward[i] = myReward[i+1];
    //  myMagOn[i] = magnetOn[i+1];
      //myRewardR[i] = myRewardR[i+1];
     // myNegReward[i] = myNegReward[i+1];
     // myVelWheel[i] = myVelWheel[i+1]; //x time series
    }

    // New location
    mx[mx.length-1] = xPos; // Update the last spot in the array with the mouse location.
    //myStimVal[myStimVal.length-1]=int(stimVoltage); 
    
    
    
    
    float startingHight = 0.85;
   // println(stimVoltage);
    myStimVal[myStimVal.length-1] = int(ScreenSizeH*(startingHight) - (magnetOn*(stimVoltage/255)*tickHeight));
    text("stimVoltage", ScreenSizeW*0.005, ScreenSizeH*(startingHight));
    
    myLick[myLick.length-1] = int(ScreenSizeH*(startingHight+0.04)  - (lickOccured*tickHeight));
    text("Lick", ScreenSizeW*0.005, ScreenSizeH*(startingHight+0.04));
    
    myRewardPeriod[myRewardPeriod.length-1] = int(ScreenSizeH*(startingHight+0.08) -(isResponseWindow*tickHeight));
    text("Response Window", ScreenSizeW*0.005, ScreenSizeH*(startingHight+0.08));
    
    myReward[myReward.length-1] = int(ScreenSizeH*(startingHight+0.12) -(waterPortOpen*tickHeight));
    text("Water Given", ScreenSizeW*0.005, ScreenSizeH*(startingHight+0.12));

  
    
    // Draw everything
    for (int i = 0; i < mx.length-1; i ++ ) {
      // Draw an ellipse for each element in the arrays. 
      // Color and size are tied to the loop's counter: i.
      strokeWeight(3);        //stroke wider   
      if (mx[i+1]==width/12) {
        continue;
      } else {

        stroke(250, 250, 250);     //stroke color
        line(mx[i+1], myStimVal[i+1], mx[i], myStimVal[i]);
        stroke(128, 0, 128);     //stroke color
        line(mx[i+1], myLick[i+1], mx[i], myLick[i]);
        stroke(0, 250, 0);     //stroke color
        line(mx[i+1], myRewardPeriod[i+1], mx[i], myRewardPeriod[i]);
        stroke(40, 0, 120);     //stroke color
        line(mx[i+1], myReward[i+1], mx[i], myReward[i]);
       // stroke(0, 250, 0);     //stroke color
       // line(mx[i+1], myRewardR[i+1], mx[i], myRewardR[i]);
       // stroke(40, 40, 40);     //stroke color
       // line(mx[i+1], myNegReward[i+1], mx[i], myNegReward[i]);
       // stroke(250, 0, 0);     //stroke color
       // line(mx[i+1], myVelWheel[i+1], mx[i], myVelWheel[i]);
      }
    }

    //velocity zero line
    strokeWeight(1);  
    stroke(155, 0, 0);     //stroke color
    line(width/12, ScreenSizeH*(startingHight), width/1.1, ScreenSizeH*(startingHight));

    //   at the edge of the window, go back to the beginning:
    if (xPos >= width/1.1) {
      xPos = width/12;
      background(0);  //Clear the screen.
    } else { 
      xPos=xPos+screenStepSize; // increment the horizontal position:
    }

    //for (int i = 0; i <activeAngle.length; i++) {
    //  if (activeAngle[i]>0) {
    //    if ((activeAngle[i])!=lastMove) {
    //      stroke(127, 127, 127);//grey
    //      strokeWeight(4);        //stroke smaller
    //      line(center.x, center.y, xEcclips[i], yEcclips[i]);
    //    } 
    //    if (((activeAngle[i])==lastMove) && (lastMove>midPointAngle)) {
    //      stroke(0, 250, 0);
    //      //  stroke(0, 0, 255);//full red
    //      strokeWeight(6);        //stroke wider
    //      line(center.x, center.y, xEcclips[i], yEcclips[i]);
    //    } else if (((activeAngle[i])==lastMove) && (lastMove<midPointAngle)) {
    //      stroke(128, 0, 128); 
    //      // stroke(255, 0, 0);//full blue
    //      strokeWeight(6);        //stroke wider
    //      line(center.x, center.y, xEcclips[i], yEcclips[i]);
    //    } else if (((activeAngle[i])==lastMove) && (lastMove==midPointAngle)) {
    //      stroke(0, 255, 0);//full blue
    //      strokeWeight(6);        //stroke wider
    //      line(center.x, center.y, xEcclips[i], yEcclips[i]);
    //    }
      }