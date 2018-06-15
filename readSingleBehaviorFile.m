path ='X:\amardinly\BehaviorData\';
dataOut=[];
dataOut.Trials = readBehaviorData([path '9122_2018_6_13_9_52_BoxRIG.txt']);
stats=getBehaviorStats(dataOut)