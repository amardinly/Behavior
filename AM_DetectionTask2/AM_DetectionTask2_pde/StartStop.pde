
void StartStop(boolean theFlag) {
  if (makeContact==false){ 
  
    if (theFlag==true) {
      println("Stop Arduino");
      myPort.write('0'); 
      canStart=false;
    } 
    else {
      println("Start Arduino");
      myPort.write('1'); 
      canStart=true;

    }
  }
}