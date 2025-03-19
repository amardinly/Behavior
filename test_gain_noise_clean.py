from alphaConvolve import alpha_convolve
import nidaqmx as ni
from nidaqmx import stream_writers
import numpy as np
import matplotlib.pyplot as plt
import time

#set parameters for testing
test_voltage = 0.4 #goal mean power
t=5
expInfo={}
expInfo['alphaRise'] = .001
expInfo['alphaDecay'] = .005
expInfo['tEPSG'] = .01
expInfo['firingRate'] = 300 
expInfo['fs'] = 5000

gmax = 0.2
while True:
    means= []
    s=time.time()
    for _ in range(10):
    	noise = alpha_convolve(gmax,
                expInfo['alphaRise'],expInfo['alphaDecay'],5,expInfo['tEPSG'],
                expInfo['fs'],expInfo['firingRate'])
    	means.append(np.mean(noise))
    print('finished test round', round(time.time()-s,5))
    mean_of_means = np.mean(means)
    if mean_of_means <= test_voltage+.02 and mean_of_means>= test_voltage-.01:
        print('found a gmax!, its',gmax,'the mean was', mean_of_means)
        break
    if mean_of_means>= test_voltage+.02:
        print('exceeded mean goal, thats no good',gmax,mean_of_means)
    gmax+=.02


means=[]
for _ in range(180):
    noise = alpha_convolve(gmax,
                expInfo['alphaRise'],expInfo['alphaDecay'],1.1,expInfo['tEPSG'],
                expInfo['fs'],expInfo['firingRate'])
    means.append(np.mean(noise))

plt.subplot(1,2,1)
plt.plot(noise[0,:])
plt.title('Example Output')
plt.ylabel('Volts')
ticks=[0,.5,1]
plt.xticks([x*expInfo['fs'] for x in ticks],ticks)
plt.xlabel('Time (s)')
plt.subplot(1,2,2)
plt.hist(means,edgecolor='k')
plt.ylabel('# Trials')
plt.xlabel('Mean Voltage Delivered')
plt.title('Simulated Trials\n Overall Mean:'+str(round(np.mean(means),2)))
plt.show()