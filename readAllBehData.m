%% Analyze entire directory of behavioral data
D='X:\amardinly\BehaviorData\';
BehDir = dir(D);  %directory for all behavior txt files 

%delete non text files from our directory 
for j = 1:size(BehDir);
    notText(j) = isempty(strfind(BehDir(j).name,'.txt'));
end
BehDir(notText) = [];

%allocate struct for all data
MasterStruct = [];


%for each file
for j = 1:numel(BehDir);
    
    
    fname = BehDir(j).name;  %file name
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
    dataOut = [];
    dataOut.Trials = readBehaviorData([D fname],0);
    
    if numel(unique(dataOut.Trials(1:end-10,2))) == 1;
        autoreward = true;
    else
        autoreward= false;
    end
    

    % put data in master struct
    MasterStruct.(mouse).(date).data = dataOut;
    MasterStruct.(mouse).(date).autoreward = autoreward;
    stats = getBehaviorStats(dataOut);
    MasterStruct.(mouse).(date).stats = stats;
 
    % save
    save('BehaviorResults','MasterStruct');
    
    
end