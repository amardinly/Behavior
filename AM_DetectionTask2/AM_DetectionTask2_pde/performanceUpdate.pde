
public void updateElapsedTime() {
  Textfield txt = ((Textfield)cp5.getController("Time"));
    txt.setValue(""+ String.format("%.2f",((time/1000))));
}

public void updateCountTotal() {
  Textfield txt = ((Textfield)cp5.getController("Total_Count"));
  txt.setValue(""+int(thisTrialNumber));
}

public void updatePerformance() {
  Textfield txt = ((Textfield)cp5.getController("P"));
  txt.setValue(""+(hitTally/(hitTally+missTally)));
}


public void updatePerformanceMISS() {
  Textfield txt = ((Textfield)cp5.getController("Miss"));
  txt.setValue(""+missTally);
}

public void updatePerformanceHIT() {
  Textfield txt = ((Textfield)cp5.getController("Hit"));
  txt.setValue(""+hitTally);
}

public void updatePerformanceFA() {
 Textfield txt = ((Textfield)cp5.getController("FA"));
 txt.setValue(""+falseAlarmTally);
}