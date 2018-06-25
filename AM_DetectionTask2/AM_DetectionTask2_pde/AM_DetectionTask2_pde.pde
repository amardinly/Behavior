import processing.serial.*; //import the Serial library
 Serial myPort;  //the Serial port object
 String val;
// since we're doing serial handshaking, 
// we need to check if we've heard from the microcontroller
boolean firstContact = false;
boolean makeContact = true;
boolean canStart = false;
boolean newTrial = false;
float previousTrialNumber = 0; 

import org.gicentre.utils.spatial.*;
import org.gicentre.utils.network.traer.physics.*;
import org.gicentre.utils.gui.*;
import org.gicentre.utils.network.traer.animation.*;
import org.gicentre.utils.geom.*;
import org.gicentre.utils.colour.*;
import org.gicentre.utils.move.*;
import org.gicentre.utils.stat.*;
import org.gicentre.utils.multisketch.*;
import org.gicentre.utils.io.*;
import org.gicentre.utils.*;
import org.gicentre.utils.text.*;
import org.gicentre.utils.network.*;
import processing.serial.*;    // import the Processing serial library //<>// //<>// //<>//
import controlP5.*;
ControlP5 cp5;
controlP5.Button b;
DropdownList d1, d2;
import org.gicentre.utils.stat.*;    // For chart classes. Library by Jo Wood.
BarChart barChart;
BarChart barChartStim;
BarChart barChartVel;

float BinnedHitTally=0;
float BinnedMissTally=0;
float BinSize=10;
int BinCrimenter = 0;
       
int serialPortNo = 2; //1 for tablets/windows, 5 for Mac
int screenStepSize =2; //2 for windows desktop 5 for tablets
int num = 200; //length of data to be displayed 200 for desktop, 100 for tablet
int tickHeight = 15; // Height of continous recording data 
int sampleRate = 115200;
                  
PrintWriter output;    // initialize the PrintWriter Java object
          
float catchTrial;
float countTrialTally=0;
float countStim=0;
boolean StimTrial = false;
        
String BoxNo = "RIG"; //Change box number to keep track of training rig being used
String currPath = "C:/BehaviorDATA/"; //D drive used on tablets
String currFolder = currPath;
              
              
float time;
String timeStr = str(time);
float startingHeightChart = 0.6;
            
boolean startedRecording = false;
            
float mx[] = new float[num]; //x time series
int myStimVal[] = new int[num]; //x time series
int myLick[] = new int[num]; //target area
int myRewardPeriod[] = new int[num]; //licking left
int myReward[] = new int[num]; //licking right
int xPos=0; //current x position
              
      
              
              
              
              
              
              
              
              
              
              //Alan's variables
              float[] magVolts = {
                0,    43,    85,   128,   170,   213,   255
              };
              
              float waterPortOpen=0;
              float magnetOn=0;
              float isResponseWindow=0;
              float lickOccured=0;
              float trialRewarded=0;
              float thisTrialNumber=0;
              float stimVoltage =0;
              float falseAlarm=0;
              boolean hitTrial = false;
              

              
            // initialize variable to store cummulative performance
            float hitTally = 0;
            float missTally = 0;
            float falseAlarmTally = 0;
            int lastTrialType=0;
            
            float hitTallyStim = 0;
            float missTallyStim = 0;
            float falseAlarmTallyStim = 0;
            float preCount=0;
            // initialize variable to store binned performance
            float BinnedhitTally = 0;
            float BinnedmissTally = 0;
            float BinnedfalseAlarmTally = 0;
            float count;
        
            float BinnedhitTallyStim = 0;
            float BinnedmissTallyStim = 0;
            float BinnedfalseAlarmTallyStim = 0;
            
            float catchTrialTally = 0;
            
            
            
              
              
              String dataReading;  // initialize variable for serial data from Arduino
              String [] dataOutput = {
              };
              
              
              
              
              int ScreenSizeW = 800; //full screen size x pixels
              int ScreenSizeH = 600; //full screen size y pixels
              
              //text box
              int sizeTextBoxW = 200;
              int sizeTextBoxH = 40;
              
            FloatList BinnedPerformance; 
            int BinWidth = 250;
            int BinHeight = 100;
            
            float TempbinnedPerformance;
            float TempbinnedPerformanceStim;
              
              
              boolean reSetBins=false;

              PVector center = new PVector(ScreenSizeW*0.3, ScreenSizeH*0.60);
































void setup() {
size(800, 700); //from600
                background(0);
                smooth();
              
                //  initialize your serial port and set the baud rate to 9600
                
      
                PFont font = createFont("arial", 9);
                PFont font2 = createFont("arial", 24); //24
              
              cp5 = new ControlP5(this);
              
                cp5.addToggle("SelectUser")
                  .setPosition(ScreenSizeW*0.7, ScreenSizeH*0.05)
                  .setSize(sizeTextBoxW/2, sizeTextBoxH)
                  .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
                  .setVisible(true)
                  ;  
                  
                cp5.addTextfield("Mouse_ID")
                  .setPosition(ScreenSizeW*0.05, ScreenSizeH*0.05)
                  .setSize(sizeTextBoxW, sizeTextBoxH)
                  .setFont(font2)
                  .setFocus(true)
                  .setColor(color(255, 0, 0))
                  .setAutoClear(false)
                  .getCaptionLabel()
                  .setFont(font);
                ;
                
                cp5.addTextfield("Box_No")
                  .setPosition(ScreenSizeW*0.33, ScreenSizeH*0.05)
                  .setSize(sizeTextBoxW/4, sizeTextBoxH)
                  //.setFont(createFont("arial", 20))
                  .setText(BoxNo)
                  .setFont(font2)
                  .setAutoClear(false)
                  .getCaptionLabel()
                  .setFont(font)
                  ;
              
                cp5.addTextfield("Answer_Duration")
                .setPosition(ScreenSizeW*0.05, ScreenSizeH*0.15)
                .setSize(sizeTextBoxW/3, sizeTextBoxH)
                // .setFont(createFont("arial", 20))
                .setText("500")
                .setDefaultValue(500)
                .setAutoClear(false)
                .setVisible(true)
                ;
                
                cp5.addTextfield("Stim Duration")
                .setPosition(ScreenSizeW*0.05, ScreenSizeH*0.25)
                .setSize(sizeTextBoxW/3, sizeTextBoxH)
                // .setFont(createFont("arial", 20))
                .setText("100")
                .setDefaultValue(100)
                .setAutoClear(false)
                .setVisible(true)
                ;
                
                 cp5.addTextfield("Time")
                .setColor(color(0, 255, 0))
                .setColorBackground(255)
                .setPosition(ScreenSizeW*0.92, ScreenSizeH*0.38)
                .setSize(sizeTextBoxW/4, sizeTextBoxH/2)
                .setText(timeStr)
                .setAutoClear(false)
                //    .setVisible(true)
                ;
            
                cp5.addToggle("Submit")
                .setPosition(ScreenSizeW*0.05, ScreenSizeH*0.45)
                .setSize(sizeTextBoxW/2, sizeTextBoxH)
                .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
                .setVisible(true)
                ;  
            
            
            
            
              //cp5.addToggle("Update")
              //  .setPosition(ScreenSizeW*0.05, ScreenSizeH*0.53)
              //  .setSize(sizeTextBoxW/4, sizeTextBoxH)
              //  .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
              //  .setVisible(true)
              //  ;  
                
                
                
            
              //cp5.addToggle("newFile")
              //  .setPosition(ScreenSizeW*0.12, ScreenSizeH*0.53)
              //  .setSize(sizeTextBoxW/4, sizeTextBoxH)
              //  .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
              //  .setVisible(true)
              //  ;  
            
            
            
              cp5.addToggle("StartStop")
                .setPosition(ScreenSizeW*0.05, ScreenSizeH*0.61)
                .setSize(sizeTextBoxW/2, sizeTextBoxH)
                .setValue(true)
                .setMode(ControlP5.SWITCH)
                .setVisible(true)
                ;
                
                
                
              //cp5.addToggle("AutoReward")
              //  .setPosition(ScreenSizeW*0.33, ScreenSizeH*0.15)
              //  .setSize(sizeTextBoxW/4, sizeTextBoxH)
              //  .setValue(false)
              //  .setVisible(true)
              //  ;
            
              //cp5.addToggle("Timeout")
              //  .setPosition(ScreenSizeW*0.41, ScreenSizeH*0.15)
              //  .setSize(sizeTextBoxW/4, sizeTextBoxH)
              //  .setValue(true)
              //  .setVisible(true)
              //  ;
                
                  cp5.addTextfield("Hit")
                .setColor(color(255, 255, 255))
                .setColorBackground(255)
                .setPosition(ScreenSizeW*0.65, ScreenSizeH*0.05)
                .setSize(sizeTextBoxW/2, sizeTextBoxH)
                .setAutoClear(false)
                .setVisible(true)
                .setFont(font2)
                .getCaptionLabel()
                .setFont(font)
                ;
                  cp5.addTextfield("Miss")
                .setColor(color(255, 255, 255))
                //  .setFont(font2)
                .setColorBackground(255)
                .setPosition(ScreenSizeW*0.65, ScreenSizeH*0.15)
                .setSize(sizeTextBoxW/2, sizeTextBoxH)
                .setAutoClear(false)
                .setVisible(true)
                .setFont(font2)
                .getCaptionLabel()
                .setFont(font)
                ;
                
                
              cp5.addTextfield("Total_Count")
                .setColor(color(0, 255, 0))
                .setColorBackground(255)
                .setPosition(ScreenSizeW*0.65, ScreenSizeH*0.25)
                .setSize(sizeTextBoxW/2, sizeTextBoxH)
                .setAutoClear(false)
                .setVisible(true)
                .setFont(font2)
                .getCaptionLabel()
                .setFont(font)
                ;
                
                
                //  cp5.addTextfield("Catch_Count")
                //.setColor(color(0, 255, 0))
                //.setColorBackground(255)
                //.setPosition(ScreenSizeW*0.65, ScreenSizeH*0.35)
                //    .setSize(sizeTextBoxW/4, sizeTextBoxH/2)
                //.setAutoClear(false)
                //.setVisible(true)
                //.setFont(font2)
                //.getCaptionLabel()
                //.setFont(font)
                //;
            
            
              cp5.addTextfield("P")
                .setColor(color(0, 0, 255))
                .setColorBackground(255)
                .setPosition(ScreenSizeW*0.8, ScreenSizeH*0.25)
                .setSize(sizeTextBoxW/4, sizeTextBoxH)
                .setDecimalPrecision(2)
                .setAutoClear(false)
                .setVisible(true)
                .setFont(font2)
                .getCaptionLabel()
                .setFont(font)
                ;
                
                
                
              cp5.addTextfield("FA")
                .setColor(color(255, 255, 255))
                .setColorBackground(255)
                .setPosition(ScreenSizeW*0.8, ScreenSizeH*0.15)
                .setSize(sizeTextBoxW/4, sizeTextBoxH)
                .setAutoClear(false)
                .setVisible(true)
                .setFont(font2)
                .getCaptionLabel()
                .setFont(font)
                ;
                
                
              
              //cp5.addBang("Reset")
              //  .setPosition(ScreenSizeW*0.92, ScreenSizeH*0.33)
              //  .setSize(sizeTextBoxW/4, sizeTextBoxH/2)
              //  .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
              //  ;  
            
              //PerformanceBarChart
              BinnedPerformance = new FloatList();
              float[] BinnedPerformanceF = BinnedPerformance.array();
            
              barChart = new BarChart (this);
              barChart.setData(BinnedPerformanceF);
              barChart.setMinValue(0);
              barChart.setMaxValue(100);
                              
                
                
    // Initialize all elements of each array to zero.
  for (int i = 0; i < mx.length; i ++ ) {
    mx[i] = 0; 
    myStimVal[i] = 0;
    myLick[i] = 0; //target area
    myRewardPeriod[i] = 0; //target area
    myReward[i] = 0; //target area

  }                     
                
                
                
                
                
                
                
                
                
  myPort = new Serial(this, Serial.list()[5], 9600);
  myPort.bufferUntil('\n'); 
}
void draw() {
  //we can leave the draw method empty, 
  //because all our programming happens in the serialEvent (see below)
    
              if (!startedRecording) { 
                text(currFolder, ScreenSizeW*0.05, ScreenSizeH*0.03);
              }
             
              
              updateElapsedTime(); 
              
              background(0);
              text(currFolder, ScreenSizeW*0.05, ScreenSizeH*0.03);
              
              updateCountTotal();
              updatePerformance();
              updatePerformanceMISS();
              updatePerformanceFA();
              updatePerformanceHIT();
                
                //bar chart of performance
              barChart.draw(ScreenSizeW*0.6, ScreenSizeH*(startingHeightChart), BinWidth, BinHeight);
              stroke(120, 120, 120); 
              strokeWeight(1);        //stroke smaller
              
                  
                
             // updatePerformanceStim();
            
                
             //bar chart setup
              line(ScreenSizeW*0.6, ScreenSizeH*(startingHeightChart), ScreenSizeW*0.6+BinWidth, ScreenSizeH*(startingHeightChart));
              text("100%", ScreenSizeW*0.57, ScreenSizeH*(startingHeightChart));
              line(ScreenSizeW*0.6, ScreenSizeH*(startingHeightChart)+(BinHeight/4), ScreenSizeW*0.6+BinWidth, ScreenSizeH*(startingHeightChart)+(BinHeight/4));
              text("75%", ScreenSizeW*0.57, ScreenSizeH*(startingHeightChart)+(BinHeight/4));
              line(ScreenSizeW*0.6, ScreenSizeH*(startingHeightChart)+(BinHeight/2), ScreenSizeW*0.6+BinWidth, ScreenSizeH*(startingHeightChart)+(BinHeight/2));
              text("50%", ScreenSizeW*0.57, ScreenSizeH*(startingHeightChart)+(BinHeight/2));
              line(ScreenSizeW*0.6, ScreenSizeH*(startingHeightChart)+(BinHeight-(BinHeight/4)), ScreenSizeW*0.6+BinWidth, ScreenSizeH*(startingHeightChart)+(BinHeight-(BinHeight/4)));
              text("25%", ScreenSizeW*0.57, ScreenSizeH*(startingHeightChart)+(BinHeight-(BinHeight/4)));
              line(ScreenSizeW*0.6, ScreenSizeH*(startingHeightChart)+(BinHeight/1), ScreenSizeW*0.6+BinWidth, ScreenSizeH*(startingHeightChart)+(BinHeight/1));
              text("0%", ScreenSizeW*0.57, ScreenSizeH*(startingHeightChart)+(BinHeight/1));
              text("binned performance", ScreenSizeW*0.7, ScreenSizeH*(startingHeightChart+0.2));
        
        
        
                
                if (BinnedHitTally+BinnedMissTally >=BinSize)  {

                  TempbinnedPerformance = (((BinnedHitTally)/BinSize)*100);
                                 // println(TempbinnedPerformance);

                  BinnedPerformance.append(TempbinnedPerformance);
                  
                  float[] BinnedPerformanceF = BinnedPerformance.array();
                  
                  barChart.setData(BinnedPerformanceF);
                  
                  BinnedHitTally = 0;
                  BinnedMissTally = 0;
                  //BinnedfalseAlarmTally = 0;
                }
           
 
              drawLines(); 
  
}