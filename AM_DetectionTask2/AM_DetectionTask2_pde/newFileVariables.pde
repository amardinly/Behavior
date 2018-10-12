public void newFileVars() {

  String mouseIDtemp = cp5.get(Textfield.class, "Mouse_ID").getText();
  String boxIDtemp = cp5.get(Textfield.class, "Box_No").getText();
  String fileName = "_"+str(year())+"_"+str(month())+"_"+str(day())+"_"+str(hour())+"_"+str(minute()); 

   
   output = createWriter(currFolder+mouseIDtemp+fileName+"_Box"+boxIDtemp+".txt"); 

 // output = createWriter("DataBuffer/"+mouseIDtemp+fileName+"_Box"+boxIDtemp+".txt");
  println(" Mouse ID = " + mouseIDtemp);
  println(" Filename = " + fileName);

  //String trimmingTemp = cp5.get(Textfield.class, "Trimming").getText();
  output.println("MouseID = " + "," + mouseIDtemp);
  output.println("BoxNo = " + "," + boxIDtemp);
  //output.println("Trimming = " + "," + trimmingTemp);
}