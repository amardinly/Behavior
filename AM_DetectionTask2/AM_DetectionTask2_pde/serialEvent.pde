void serialEvent( Serial myPort) {
//put the incoming data into a String - 
//the '\n' is our end delimiter indicating the end of a complete packet
val = myPort.readStringUntil('\n');
//make sure our data isn't empty before continuing
if (val != null) {
  //trim whitespace and formatting characters (like carriage return)
    val = trim(val);
 // println(val);
}
  //look for our 'A' string to start the handshake
  //if it's there, clear the buffer, and send a request for data
  
if (firstContact == false) {
    if (val.equals("A")) {
      myPort.clear();
      firstContact = true;
      myPort.write("A");
      println("contact");
      makeContact = false;
    }
  }



if (canStart) {
   output.println(val);  // write the output to .txt file as string (will just be number in text)
   println(val);  // print trigger times to this display
   
    String[] items = split(val, ','); //split the string into multiple strings where there is a ","
    float[] values = float(items);



   if (values.length >= 6) { 
     time = values[0];
     thisTrialNumber = values[1];
     trialRewarded = values[2];
//     println(trialRewarded);
     lickOccured = values[3];
  //   println(lickOccured);

     stimVoltage = values[4];
     isResponseWindow = values[5];
     magnetOn = values[6];
     waterPortOpen = values[7];
     falseAlarm = values[8];
    //println(falseAlarm);
     
     updateBehaviorStats(); 
     }
   }
}