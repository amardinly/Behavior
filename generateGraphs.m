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
s=find(sum(isnan(MasterHits),2) == size(MasterHits,2));  %find training days where there are only nans
e=s(1)-1;   %get the last training day where there is data
days = 1:e;  %create a time vector for plotting

MasterDp(isinf(MasterDp))=0;


figure()
subplot(1,2,1);

errorbar(days,nanmedian(MasterHits(1:e,:),2),stderr(MasterHits(1:e,:)'),'k-');


ylim([0 1])
hold on
errorbar(days,nanmedian(MasterFA(1:e,:),2),stderr(MasterFA(1:e,:)'),'r-');

for n=1:size(MasterHits,2);
    plot(days,MasterHits(1:e,n),'color',[0 0 0 .2]);
    plot(days,MasterFA(1:e,n),'color',[1 0 0 .2]);
end

xlabel('Training Days');
ylabel('Hit / FA Rate');


subplot(1,2,2);
errorbar(days,nanmedian(MasterDp(1:e,:),2),stderr(MasterDp(1:e,:)'),'b-');
hold on
for n=1:size(MasterHits,2);
    plot(days,MasterDp(1:e,n),'color',[0 0 1 .2]);
end

%% Plot PsyCurve
figure()
for j = 1:numel(miceNames);
    u = 1;
    theData=MasterStruct.(miceNames{j});
    dates=fieldnames(theData);
    for i = 1:numel(dates);
        thisData = theData.(dates{i});
        
        if thisData.autoreward == 0 && (size(thisData.stats.psy,1)>2);
            PC{u}=thisData.stats.psy;
            DATUM{u}=thisData.data.Trials;
            u=u + 1;
        end
        
    end
end

for a = 1:numel(PC);
    plot(PC{a}(:,1),PC{a}(:,2),'color',[0 0 0 .6]);
    hold on;
end
ylim([0 1]);
xlabel('Stim Strength');
ylabel('Hit Rate'); 

% %% Analyze Subsampled PCs
% 
% data=DATUM{6};
% cutoff = 100;
% 
% 
% stimvals = unique(batch2(:,1));
% 
% for k = 1:numel(stimvals);  %for each unique stimulus
%     samples1 = find(data(1:cutoff,1)==stimvals(k));
%     samples2 = find(data(cutoff+1:end,1)==stimvals(k));
%     samples3 = find(data(:,1)==stimvals(k));
% 
%     PsyCurve(k,1)=stimvals(k);  %stimulus Valus
%     PsyCurve(k,2)=mean(data(samples1,2));  % % correct (hitrate)    
%     PsyCurve(k,3)=mean(data(samples2+cutoff,2));  % % correct (hitrate)    
%     PsyCurve(k,4)=mean(data(samples3,2));
%     
% end
% 
% 
% % 4 = total
% % 2 = early
% % 3 = remainder
% % 
% % ft = fittype( 'a*exp(-b*x)+c', 'independent', 'x', 'dependent', 'y' );
% % opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
% % opts.Display = 'Off';
% % opts.StartPoint = [0.590222413778962 0.0704486468813598 0.973179827025178];
% % [fitresult, gof] = fit(  PsyCurve(:,1),  PsyCurve(:,4), ft, opts );
% % figure();
% % plot( fitresult, PsyCurve(:,1), PsyCurve(:,4) ,'k');
% % hold on
% % plot(PsyCurve(:,1),PsyCurve(:,4),'ko')
% 
% hold on
% 
% h=figure()
% plot(PsyCurve(:,1),PsyCurve(:,4),'k');  %total data
% 
% ft = fittype( 'a*exp(-b*x)+c', 'independent', 'x', 'dependent', 'y' );
% opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
% opts.Display = 'Off';
% opts.StartPoint = [0.590222413778962 0.0704486468813598 0.973179827025178];
% [fitresult, gof] = fit(  PsyCurve(:,1),  PsyCurve(:,2), ft, opts );
% 
% ft = fittype( 'a*exp(-b*x)+c', 'independent', 'x', 'dependent', 'y' );
% opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
% opts.Display = 'Off';
% opts.StartPoint = [0.590222413778962 0.0704486468813598 0.973179827025178];
% [fitresult2, gof] = fit(  PsyCurve(:,1),  PsyCurve(:,3), ft, opts );
% 
% hold on;
% plot(fitresult2);
% plot(fitresult);
% 
% 
