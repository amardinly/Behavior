function Trials = readBehaviorData(filename,plotOpt);
if nargin<2;
    plotOpt = 0;
end

% path = 'X:\amardinly\BehaviorData\';

A = importdata([filename],',',2);

trialStarts = find(diff(A.data(:,1))<0);  %find when time goes negative

numberOfTrials = (unique(A.data(:,2)));
numberOfTrials(isnan(numberOfTrials))=[];
numberOfTrials=numberOfTrials(end);

for j = 1:(numberOfTrials);  %for each trial
    trialSamples = find(A.data(:,2)==j);
    trialSamples(end) = [];

    Trials(j,1) = mode(A.data(trialSamples,5));  %stimulus value
    Trials(j,2) = max(A.data(trialSamples,3));  %rewarded
    Trials(j,3) = max(A.data(trialSamples,4) & A.data(trialSamples,6));   %licked during response window
    Trials(j,4) = max(A.data(trialSamples,4));   %licked occured during trial
    
% 4) lick occured
% 6) is response window


end
% 
% stimvals = unique(Trials(:,1));
% for k = 1:numel(stimvals);  %for each unique stimulus
%     samples = find(Trials(:,1)==stimvals(k));
%     PsyCurve(k,1)=stimvals(k);  %stimulus Valus
%     PsyCurve(k,2) = mean(Trials(samples,2));  % % correct (hitrate)
%     PsyCurve(k,3) = (sum(Trials(:,1)==stimvals(k)));    %trial number
% end
% 
% 
% if size(PsyCurve,2)>5;
% ft = fittype( 'a*exp(-b*x)+c', 'independent', 'x', 'dependent', 'y' );
% opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
% opts.Display = 'Off';
% opts.StartPoint = [0.590222413778962 0.0704486468813598 0.973179827025178];
% [fitresult, gof] = fit(  PsyCurve(:,1),  PsyCurve(:,2), ft, opts );
% if plotOpt;
%     figure();
%     plot( fitresult, PsyCurve(:,1), PsyCurve(:,2) );
%     hold on
%     plot(PsyCurve(:,1),PsyCurve(:,2),'ko')
% end
% dataOut.PsyCurve = PsyCurve;
% dataOut.SigFit = fitresult;
% dataOut.fitStats = gof;
% end
% 
% if plotOpt
%     figure()
%     hold on
%     for j = 1:numberOfTrials;
%            trialSamples = find(A.data(:,2)==j); %timebase seconds
%            time = A.data(trialSamples,1)/1000; 
%            
%            [lickHigh] = find(diff(A.data(trialSamples,4)>0));
%            scatter(time(lickHigh),A.data(trialSamples(lickHigh),4)+j-1,100,'m.');
%            
%  
%            
%            [response] = find(A.data(trialSamples,6));
%            plot(time(response),A.data(trialSamples(response),6)+.2+j-1,'g');
%            
%             
%            [stim] = find(A.data(trialSamples,7));
%            plot(time(stim),A.data(trialSamples(stim),7)+j-1,'k');
%                         
%            [reward] = find(A.data(trialSamples,8));
%            scatter(time(reward),A.data(trialSamples(reward),8)-.2+j-1,1000,'b.');
%            
%     end
% end
%     
%     
%     
% %col orders
% 
% % 1) millis -trialstartime
% % 2 this trial number
% % 3) trial rewarded
% % 4) lick occured
% % 5) stimval
% % 6) is response window
% % 7) mag on
% % 8) waterport open
% % 9) false alarm
% 
% % %% make trial figures
% % t=t+1;
% close;
% figure();
% hold on;
% time = A.data(trialSamples,1)/1000;
% % plot(time,A.data(trialSamples,2),'c') %trial #
% plot(time,A.data(trialSamples,3),'y') %trial rewarded
% % plot(,'r') %T
% plot(time,A.data(trialSamples,4),'m') %licks
% plot(time,A.data(trialSamples,8),'b') %reward value
% plot(time,A.data(trialSamples,7),'k') %mag value
% plot(time,A.data(trialSamples,9),'r--') %false alaram value
% plot(time,A.data(trialSamples,6),'g--') %is response window