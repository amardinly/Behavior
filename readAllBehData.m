%% Analyze entire directory of behavioral data
D='X:\amardinly\BehaviorData\';
BehDir = dir(D);


for j = 1:size(BehDir);
    notText(j) = isempty(strfind(BehDir(j).name,'.txt'));
end

BehDir(notText) = [];

MasterStruct = [];

for j = 1:numel(BehDir);
    
    
    fname = BehDir(j).name;
    
    disp(['Analyzing ' fname]);
    
    [tok rem] = strtok(fname,'_');
    
    mouse = tok;
    mouse = ['m' mouse];
    
    [year rem] = strtok(rem,'_');
    [month rem] = strtok(rem,'_');
    [day rem] = strtok(rem,'_');
    if numel(month) == 1; month = ['0' month]; end;
    if numel(day) == 1; day = ['0' day]; end;
    
    date=['x' year month day];
    
    dataOut = readBehaviorData([D fname],0);
    
    if numel(unique(dataOut.Trials(:,2))) == 1;
        autoreward = true;
    else
        autoreward= false;
    end
    
    
    
    try
    % put data in master struct
    
    MasterStruct.(mouse).(date).data = dataOut;
    MasterStruct.(mouse).(date).autoreward = autoreward;

    stats = getBehaviorStats(dataOut);
    
    MasterStruct.(mouse).(date).stats = stats;
    catch
    disp(['error- could not save ' fname ' due to syntax stupidity']) 
    end

    
    % save
    save('BehaviorResults','MasterStruct');
    
    
end