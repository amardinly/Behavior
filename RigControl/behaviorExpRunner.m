savePath = 'Z:\frankenshare\hayley\PTFiles\'

formatOut = 'yymmdd';
date=num2str(datestr(now,formatOut));

addpath(genpath('C:\Users\MOM2\Documents\GitHub\ClosedLoopDaq\'));
do_udp=0;

ExpStruct.mouseID = input('please enter mouse ID: ','s');
ExpStruct.notes = input('please enter relevant info: ' ,'s');
savePath2 = [savePath date '\' ExpStruct.mouseID '\'];
if ~exist(savePath2, 'dir')
    mkdir([savePath date '\'])
    mkdir(savePath2);
end
savePath=savePath2;
[ ExperimentName ] = autoExptname1(savePath, ExpStruct.mouseID);


s = daq.createSession('ni'); %ni is company name
addAnalogInputChannel(s,'Dev3',0,'Voltage');
%addAnalogOutputChannel(s,'Dev3',1,'Voltage');
addTriggerConnection(s,'External','Dev3/PFI4','StartTrigger');  %trigger connection from psy

addDigitalChannel(s, 'Dev3','port0/line15','InputOnly'); %stim on/off
addDigitalChannel(s, 'Dev3','port0/line13','InputOnly');
addDigitalChannel(s, 'Dev3','port0/line10','InputOnly'); %running
addDigitalChannel(s, 'Dev3','port0/line8','InputOnly'); %water
addDigitalChannel(s, 'Dev3','port0/line9','InputOnly'); %lick


addDigitalChannel(s,'Dev3','Port0/Line5','OutputOnly');  %camera
addAnalogInputChannel(s,'Dev3',1,'Voltage'); %scan image frames

s.Rate=20000;
s.ExternalTriggerTimeout=180; 
output = zeros(20000,1);
%addDigitalChannel(s,'Dev3','Port0/Line5','OutputOnly');   %camera?


%s.Rate=20000;
%s.ExternalTriggerTimeout=30; %basically never time out

CameraTrigger=makepulseoutputs(1,60,.5,1,30,20000,2);

if do_udp
    try; echoudp('on',55000); catch; disp('error initializing UDP - if already running, ignore');  end;
    try; fclose(myUDP); end;
    myUDP = udp('128.32.177.229',55000);
    fopen(myUDP);
end
% fwrite(myUDP,num2str(i+1));
i=1
going =1
dataIn = [];
hit = 0;
miss = 0;
fa=0;
cr=0;
while going
   if do_udp
       fwrite(myUDP,num2str(i));HB41
   end
   
   s.queueOutputData(CameraTrigger);

try
    dataIn = s.startForeground();   %run a sweep
    disp('cleared sweep');
catch
    save([savePath ExperimentName],'ExpStruct');
    going=0;
end
    fprintf('sweep completed \n');
ExpStruct.inputs{i} = dataIn;
figure(5);plot(dataIn(:,[2 5 6]))
if length(find(diff(dataIn(:,2))))>0
    if length(find(diff(dataIn(:,5)))) > 0
        hit=hit+1;
    else
        miss=miss+1;
    end
else
    if length(find(diff(dataIn(:,6)))) > 0
        fa=fa+1;
    else
        cr=cr+1;
    end
end
i=i+1
disp('hit percent: ');
disp(hit/(hit+miss));
disp('fa percent: ');
disp(fa/(cr+fa));
end
% displayTriggers(outputSignal,i);

save([savePath ExperimentName],'ExpStruct');
disp('saved!')