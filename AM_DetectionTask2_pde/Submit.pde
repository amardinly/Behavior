void Submit(boolean theFlag) {
  if (makeContact==false){ 
    String[] submitvals = new String[13];
    submitvals[0]="x";
    submitvals[1] = cp5.get(Textfield.class, "%size_one").getText();
    submitvals[2] = "z";
    submitvals[3] = cp5.get(Textfield.class, "%size_two").getText();
    submitvals[4] = "c";
    submitvals[5] = cp5.get(Textfield.class, "black_level").getText();
    submitvals[6] = "b";
    submitvals[7] = cp5.get(Textfield.class, "state").getText();
    submitvals[8] = "s";
    submitvals[9] = cp5.get(Textfield.class, "do_opto").getText();
    submitvals[10] = "o";
    submitvals[11] = cp5.get(Textfield.class, "do_alt_isi").getText();
    submitvals[12] = "i";
    
    String joinedvals = join(submitvals,"");
    

    myPort.write(joinedvals);
      delay(600);
      println("star");
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