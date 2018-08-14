

void WaterPrompt(boolean theFlag) {
  //if(millis()-start_time<1000){return;} 
  if (makeContact==false & canStart == false){ 
    println("water prompt");
    if (theFlag==true) {
      myPort.write('2');
    }
  }
}