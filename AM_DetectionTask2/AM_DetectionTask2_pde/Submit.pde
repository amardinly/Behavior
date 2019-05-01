void Submit(boolean theFlag) {
  if (makeContact==false){ 
    String[] submitvals = new String[7];
    submitvals[0]="x";
    submitvals[1] = cp5.get(Textfield.class, "%size").getText();
    submitvals[2] = "z";
    submitvals[3] = cp5.get(Textfield.class, "black_level").getText();
    submitvals[4] = "b";
    submitvals[5] = cp5.get(Textfield.class, "state").getText();
    submitvals[6] = "s";
    String joinedvals = join(submitvals,"");
    myPort.write(joinedvals);
      delay(600);
      //String newval = myPort.readStringUntil('\n');
      //while (newval==null){
      //  newval = myPort.readStringUntil('\n');
      //}
      //trim whitespace and formatting characters (like carriage return)
      //wval = trim(newval);
      //intln("hey sent!");
      //if (newval.equals("Q")){
      //  println("got q");
      //}
    if (theFlag==true) {
    newFileVars();
    delay(100);
    println("ready");
    } 
    else {


    }
  }
}