path ='X:\amardinly\BehaviorData\';
dataOut=[];
dataOut.Trials = readBehaviorData([path '9149_2018_6_21_17_9_BoxRIG.txt']);
stats=getBehaviorStats(dataOut)

% 
% [coeffs, x, curve1, threshold1]=FitPsycheCurveLogit(stats.psy(:,1),stats.psy(:,2).*stats.psy(:,3),stats.psy(:,3));
% % figure();
% plot(curve1(:,1),curve1(:,2),'color',[i 0 0]);
% hold on;
% plot(stats.psy(:,1),stats.psy(:,2)*100,'o','color',[i 0 0 ]);
% 
% i = i + .2;