s=serial('COM7','BaudRate',9600);
fopen(s);
readData=fscanf(s) %reads "A"
flushinput(s);fprintf(s,'%s\n','fff','sync');
fprintf(s,'%s\n','1','sync');readData=fscanf(s)

fclose(s);