%% Generate Learning Curves for each mouse
miceNames = fieldnames(MasterStruct);
MasterHits = nan(15,numel(miceNames)); %preallocate
MasterFA = nan(15,numel(miceNames));
MasterDp = nan(15,numel(miceNames));



for j = 1:numel(miceNames);
    trainday = 0;
    
    
    theData=MasterStruct.(miceNames{j});
    
    dates=fieldnames(theData);
    clear numDates
    for v=1:numel(dates);
        numDates(v)=str2num(dates{v}(2:end));
    end
    [iv ivi]=sort(numDates);
    dates = dates(ivi);
    
    
    for i = 1:numel(dates);
        thisData = theData.(dates{i});
        
        if thisData.autoreward == 0;
            trainday = trainday + 1;
            
            MasterHits(trainday,j) = thisData.stats.HitRate;
            MasterFA(trainday,j) =  thisData.stats.FArate;
            MasterDp(trainday,j) =  thisData.stats.DprimeSimple;
        end
        
    end
end

%% Plot Summary data

mHits = .7;
%only include mice that hit .7 or higher one day
i=1;
for j=1:size(MasterHits,2)
    
    maxHit = max(MasterHits(:,j));
    if maxHit<mHits || isnan(mHits);
        toDel(i)=j;
        i=i+1;
    end
    
    
end


MasterHits(:,toDel)=[];

MasterDp(:,toDel)=[];

MasterFA(:,toDel)=[];







s=find(sum(isnan(MasterHits),2) == size(MasterHits,2));  %find training days where there are only nans
e=s(1)-1;   %get the last training day where there is data
days = 1:e;  %create a time vector for plotting



figure()
subplot(1,2,1);

errorbar(days,nanmean(MasterHits(1:e,:),2),stderr(MasterHits(1:e,:)'),'k-');


ylim([0 1])
hold on
errorbar(days,nanmean(MasterFA(1:e,:),2),stderr(MasterFA(1:e,:)'),'r-');

for n=1:size(MasterHits,2);
    plot(days,MasterHits(1:e,n),'color',[0 0 0 .2]);
    plot(days,MasterFA(1:e,n),'color',[1 0 0 .2]);
end

xlabel('Training Days');
ylabel('Hit / FA Rate');


subplot(1,2,2);
errorbar(days,nanmean(MasterDp(1:e,:),2),stderr(MasterDp(1:e,:)'),'b-');
hold on
for n=1:size(MasterHits,2);
    plot(days,MasterDp(1:e,n),'color',[0 0 1 .2]);
end

%% Plot PsyCurve
clear PC DATUM

for j = 1:numel(miceNames);
    theData=MasterStruct.(miceNames{j});
    dates=fieldnames(theData);
    for i = 1:numel(dates);
        thisData = theData.(dates{i});
        
        if thisData.autoreward == 0 && (size(thisData.stats.psy,1)>2) && max(thisData.stats.psy(:,2)>.7);
            
            
            PC{j,i}=thisData.stats.psy;
            DATUM{j,i}=thisData.data.Trials;
            
            pflag(j,i)=1;
        else
            
            pflag(j,i)=0;
            
            PC{j,i}=[];
            DATUM{j,i}=[];
        end
        
    end
end
%%
figure()
PC = PC(:);
pflag = pflag(:);

PC=PC(find(pflag));

for a = 1:numel(PC);
    plot(PC{a}(:,1),PC{a}(:,2),'.-','color',[0 0 0 .6]);
    
    if size(PC{a}(:,2),1)==8;
        allPC(:,a)=PC{a}(:,2);
    else
        allPC(:,a)=nan(1,8);
    end
    hold on;
end
ylim([0 1]);
xlabel('Stim Strength');
ylabel('Hit Rate');
hold on;
errorbar(PC{a}(:,1),nanmean(allPC,2),stderr(allPC'),'ro-','LineWidth',3);

%% Analyze Subsampled PCs
DATUM = DATUM(:);
DATUM=DATUM(find(pflag));


%%  Estiamte psycurve from early trials
clear P50_Err Slope_Err

for run = 1:numel(DATUM);
    data=DATUM{run};
    
    n=1;
    for cutoff = 20:20:200;
        
        
        clearvars -except DATUM n cutoff data run curvef Slope_Err P50_Err thresholdf;
        stimvals = unique(data(:,1));
        
        for k = 1:numel(stimvals);  %for each unique stimulus
            samples1 = find(data(1:cutoff,1)==stimvals(k));
            samples2 = find(data(cutoff+1:end,1)==stimvals(k));
            samples3 = find(data(:,1)==stimvals(k));
            
            Weights(k,1) = numel(samples1);
            Weights(k,2) = numel(samples2);
            Weights(k,3) = numel(samples3);
            
            PsyCurve(k,1)=stimvals(k);  %stimulus Valus
            PsyCurve(k,2)=mean(data(samples1,2));  % % correct (hitrate)
            PsyCurve(k,3)=mean(data(samples2+cutoff,2));  % % correct (hitrate)
            PsyCurve(k,4)=mean(data(samples3,2));
            
        end
        
        
        %fit FULL CURVE
        if cutoff==20;
            [coeffs, stats, curvef, thresholdf]=FitPsycheCurveLogit(PsyCurve(:,1),PsyCurve(:,4).*Weights(:,3),Weights(:,3));
        end
        
        try
            %fit first section
            [coeffs, stats, curve1, threshold1]=FitPsycheCurveLogit(PsyCurve(:,1),PsyCurve(:,2).*Weights(:,1),Weights(:,1));
        catch
            curve1=nan;
            threshold = nan;
        end
        
        if ~isnan(curve1);
            
            plot(curvef(:,1),curvef(:,2),'LineWidth',3);
            hold on;
%             plot(curve1(:,1),curve1(:,2),'r');
            scatter(PsyCurve(:,1),PsyCurve(:,4)*100);
            
            P50f=thresholdf(2);
            P501=threshold1(2);
            
            Slopef=(thresholdf(3)-thresholdf(1))/2;
            Slope1=(threshold1(3)-threshold1(1))/2;
            
            P50_Err(n,run)=abs(P50f-P501);
            
            Slope_Err(n,run)=abs(Slopef-Slope1);
            
        else;
            P50_Err(n,run)=100;
            Slope_Err(n,run) = 100;
            
            
        end
        
        
        n=n + 1;
    end
    
    
end
%% plot results

cu=20:20:200;
P50_Err=(P50_Err/255)*100;  %express ad percent of max stim
Slope_Err=(Slope_Err/255)*100;  %express ad percent of max stim

figure();
subplot(1,2,1)
errorbar(cu,nanmedian(P50_Err,2),stderr(P50_Err'),'.-')
hold on
for j = 1:size(P50_Err,2)
    plot(cu,P50_Err(:,j),'color',[.4 .4 .4 .4]);
end

xlabel('Sample Trials');
ylabel('P50 estimation error (percent)')

subplot(1,2,2)
errorbar(cu,nanmedian(Slope_Err,2),stderr(Slope_Err'),'.-')
hold on
for j = 1:size(P50_Err,2)
    plot(cu,Slope_Err(:,j),'color',[.4 .4 .4 .4]);
end

xlabel('Sample Trials');
ylabel('Slope estimation error (percent)')
xlim([0 max(cu)])

%% Generate 95% CIs for assessing statistical significance of PC shifts
clear SlopeEstimate E50Estimate
for R = 1:numel(DATUM);
    clearvars -except R DATUM SlopeEstimate E50Estimate;
    
    data=DATUM{R};  %get data from 1
    JJJ = 1;
   for  pcnt_opto = 5:5:50;
    
    for niter = 1:10000;  %random smaples
        
        
        
        stimvals = unique(data(:,1));
        for k = 1:numel(stimvals);  %for each unique stimulus
            
            
            samples = find(data(:,1)==stimvals(k));
            rp = randperm(numel(samples));
            samples=samples(rp);
            
            cutoff = round(size(samples,1)/(100/pcnt_opto));
            
            Osamples = samples(1:cutoff);
            Csamples = samples(cutoff+1:end);
            
            Weights(k,1) = numel(Osamples);
            Weights(k,2) = numel(Csamples);
            
            PsyCurve(k,1)=stimvals(k);  %stimulus Valus
            PsyCurve(k,2)=mean(data(Osamples,3));  % % correct (hitrate)
            PsyCurve(k,3)=mean(data(Csamples,3));  % % correct (hitrate)
            
        end
        
        
        
        [coeffs, stats, curveO, thresholdO]=FitPsycheCurveLogit(PsyCurve(:,1),PsyCurve(:,2).*Weights(:,1),Weights(:,1));
        [coeffs, stats, curveC, thresholdC]=FitPsycheCurveLogit(PsyCurve(:,1),PsyCurve(:,3).*Weights(:,2),Weights(:,2));
        
        
        MasterOCurve(:,niter) = curveO(:,2);
        MasterCCurve(:,niter) = curveC(:,2);
        
        SlopeO(niter)=(thresholdO(3)-thresholdO(1))/2;
        SlopeC(niter)=(thresholdC(3)-thresholdC(1))/2;
        
        P50O(niter)=thresholdO(2);
        P50C(niter)=thresholdC(2);
        
        if mod(niter,100)==0;
            disp(['iter # ' num2str(niter) ' on dataset ' num2str(R) ' with ' num2str(pcnt_opto) ' pcnt opto']);
        end
    end
    
    plotOpt = 0; 
    if plotOpt;
        
        ts = tinv([0.025  0.975],size(MasterOCurve,2)-1);
        figure()
        plot(curveO(:,1),mean(MasterOCurve,2),'r','LineWidth',3)
        hold on
        plot(curveO(:,1),mean(MasterOCurve,2)+(ts(1)*stderr(MasterOCurve'))','r--')
        plot(curveO(:,1),mean(MasterOCurve,2)+(ts(2)*stderr(MasterOCurve'))','r--')
        
        plot(curveC(:,1),mean(MasterCCurve,2),'k','LineWidth',3)
        hold on
        plot(curveC(:,1),mean(MasterCCurve,2)+(ts(1)*stderr(MasterCCurve'))','k--')
        plot(curveC(:,1),mean(MasterCCurve,2)+(ts(2)*stderr(MasterCCurve'))','k--')
        
        for j = 1:1000;
            plot(curveO(:,1),MasterOCurve(:,j),'color',[1 0 0 .2])
            hold on
            plot(curveO(:,1),MasterCCurve(:,j),'color',[0 0 0 .2])
            
        end
        
        
        
        figure()
        histogram(P50O-mean(P50C),25)
        
        figure()
        histogram(SlopeO-mean(SlopeC),25)
    end
    
    P50O(P50O>225) = nan;
    P50C(P50C>225) = nan;
    P50O(P50O<0) = 0;
    P50C(P50C<0) = 0;
    
    SlopeO(SlopeO>300) = nan;
    SlopeO(SlopeO>300) = nan;
    SlopeC(SlopeC<0) = nan;
    SlopeC(SlopeC<0) = nan;

    
    E50Estimate(R,JJJ) = prctile(abs(P50O-mean(P50C)),95)/255;
    SlopeEstimate(R,JJJ) = prctile(abs(SlopeO-mean(SlopeC)),95)/255;
    JJJ=JJJ+1;
   end
end
%%
opc=5:5:50;
figure(); plot(opc,E50Estimate','color',[.4 .4 .4]);
hold on; plot(opc,nanmean(E50Estimate',2),'k','LineWidth',4);
xlabel('Pcnt trials with manipulation')
ylabel('Fraction of change detectable relative to control')
title('Estimation shifts in Detection threshold');
ylim([0 1])
figure(); plot(opc,SlopeEstimate','color',[.4 .4 .4]);
hold on; plot(opc,nanmedian(SlopeEstimate',2),'k','LineWidth',4);
xlabel('Pcnt trials with manipulation')
title('Estimation shifts in PC Slope');
ylabel('Fraction of change detectable relative to control')
ylim([0 1])

save('Power Calculation','E50Estimate','SlopeEstimate','opc');