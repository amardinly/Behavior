load('summaryData_06192018.mat')


figure()
subplot(1,2,1)
plot(nanmean(h,2))
errorbar(nanmean(h(1:8,:),2),stderr(h(1:8,:)'),'k','LineWidth',2)
hold on
errorbar(nanmean(f(1:8,:),2),stderr(f(1:8,:)'),'r','LineWidth',2)
ylim([0 1]);
xlim([0 9]);
xlabel('Training Days')
ylabel('Hit / FA Rate');

subplot(1,2,2)
errorbar(nanmean(d(1:8,:),2),stderr(d(1:8,:)'),'b','LineWidth',2)
xlim([0 9]);
ylim([0 3]);
xlabel('Training Days')
ylabel('Dprime');
%%
figure()
for j = 1:size(on,1)
plot([on(j,1),off(j,1)],'color',[0 0 0 .2]);
hold on
plot([on(j,2),off(j,2)],'color',[1 0 0 .2]);
end

errorbar([1 2],[mean(on(:,1)) mean(off(:,1))],[stderr(on(:,1)) stderr(off(:,1))],'k','LineWidth',3)
errorbar([1 2],[mean(on(:,2)) mean(off(:,2))],[stderr(on(:,2)) stderr(off(:,2))],'r','LineWidth',3)
axis square;
xlim([.8 2.2]);
set(gca,'Xtick',[]);
ylim([0 1]);
ylabel('Hit / FA Rate')