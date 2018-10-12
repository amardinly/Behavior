
void MagnetPulse(boolean theFlag) {
  //if(millis()-start_time<1000){return;} //this prevents weird running on start up
  if (makeContact==false & canStart == false){ 
    println("magnet pulse");
    if (theFlag==true) {
      myPort.write('3');
    }
  }
}