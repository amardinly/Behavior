public void newFileVars() {

  String mouseIDtemp = cp5.get(Textfield.class, "Mouse_ID").getText();
  String boxIDtemp = cp5.get(Textfield.class, "Box_No").getText();
  String statetemp = cp5.get(Textfield.class, "state").getText();
  String bltemp = cp5.get(Textfield.class, "black_level").getText();
  String sztemp = cp5.get(Textfield.class, "%size_one").getText();
  String sztemp2 = cp5.get(Textfield.class, "%size_two").getText();
  String optotemp = cp5.get(Textfield.class, "do_opto").getText();
  String fileName = "_"+str(year())+"_"+str(month())+"_"+str(day())+"_"+str(hour())+"_"+str(minute())+"_state_"+statetemp+"_bllevel_"+bltemp+"_size1_"+sztemp +"_size2_"+sztemp2 + "_opto_"+optotemp; 

   
   output = createWriter(currFolder+mouseIDtemp+fileName+"_Box"+boxIDtemp+".txt"); 

 // output = createWriter("DataBuffer/"+mouseIDtemp+fileName+"_Box"+boxIDtemp+".txt");
  println(" Mouse ID = " + mouseIDtemp);
  println(" Filename = " + fileName);

  //String trimmingTemp = cp5.get(Textfield.class, "Trimming").getText();
  output.println("MouseID = " + "," + mouseIDtemp);
  output.println("BoxNo = " + "," + boxIDtemp);
  //output.println("Trimming = " + "," + trimmingTemp);
}