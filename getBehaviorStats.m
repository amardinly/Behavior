function stats=getBehaviorStats(dataOut);
Trials = dataOut.Trials;
qThreshold = 25;
QuitTrial = nan;
q = 0;
for j = 1:size(Trials,1);
   if Trials(j,3) == 0; %increiment no lick counter by 1
       q=q+1;
   else %if lick, reset
       q=0;
   end
   
   if q>=qThreshold;
      QuitTrial = j;  
   end
end

if ~isnan(QuitTrial);
   Trials=Trials(1:QuitTrial-qThreshold,:);    
end


stimvals = unique(Trials(:,1));
for k = 1:numel(stimvals);  %for each unique stimulus
    samples = find(Trials(:,1)==stimvals(k));
    PsyCurve(k,1)=  stimvals(k);  %stimulus Valus
    PsyCurve(k,2) = mean(Trials(samples,3));  % % correct (hitrate)   
    PsyCurve(k,3) = (sum(Trials(:,1)==stimvals(k)));    %trial number
end

k = find(PsyCurve(:,1)==255);

 stats.HitRate = PsyCurve(k,2);
 stats.MissRate = 1-PsyCurve(k,2);
 
k = find(PsyCurve(:,1)==0);
if isempty(k);
 
stats.FArate = nan;
stats.CRrate = nan;
else
    
stats.FArate = PsyCurve(k,2);
stats.CRrate = 1-PsyCurve(k,2); 
    
end

if isempty(k);
stats.DprimeStrong = nan;
stats.DprimeTotal =nan;
else
stats.DprimeSimple = norminv(stats.HitRate ) - norminv(stats.FArate);


allStimHits = sum(PsyCurve(:,2).*PsyCurve(:,3))/sum(PsyCurve(:,3));


stats.DprimeTotal = norminv( allStimHits   ) - norminv(stats.FArate);
end

stats.nTrials = size(dataOut.Trials,1);
stats.psy = PsyCurve;


PsyCurve(1,1) = 255;   PsyCurve(1,2) = .78; PsyCurve(1,3) = 44;
PsyCurve(2,1) = 100;   PsyCurve(2,2) = .68; PsyCurve(2,3) = 24;
PsyCurve(3,1) = 90;   PsyCurve(3,2) = .58; PsyCurve(3,3) = 14;
PsyCurve(4,1) = 56;   PsyCurve(4,2) = .48; PsyCurve(4,3) = 54;
PsyCurve(5,1) = 25;   PsyCurve(5,2) = .38; PsyCurve(5,3) = 74;
PsyCurve(6,1) = 0;   PsyCurve(6,2) = .2; PsyCurve(6,3) = 44;
