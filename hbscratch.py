import numpy as np
import matplotlib.pyplot as plt
import time

#set parameters for testing
test_voltage = 0.25 #goal mean power
t=5
expInfo={}
extraInfo={}
expInfo['alphaRise'] = .001
expInfo['alphaDecay'] = .005
expInfo['tEPSG'] = .01
expInfo['firingRate'] = 300 
expInfo['fs'] = 5000

extraInfo['fs'] = 5000
extraInfo['gamma_rate']=10
extraInfo['blue_delay']=4
extraInfo['red_volts']=.3
extraInfo['blue_volts']=3
opto_length_s=1.5
opto_length=int(np.floor(opto_length_s * extraInfo['fs']))
Fs=extraInfo['fs']
opto_vec=np.arange(opto_length)/Fs
gamma_rate = extraInfo['gamma_rate']

redGamma = np.abs(np.sin(np.pi*gamma_rate*opto_vec));
redGamma = (redGamma/np.mean(redGamma))*extraInfo['red_volts']
blueGamma = np.abs(np.sin(np.pi*gamma_rate*(opto_vec - extraInfo['blue_delay'])));
blueGamma = (blueGamma/np.mean(blueGamma))*extraInfo['blue_volts'];
arr=np.vstack([blueGamma,redGamma])
arr[:,-100:]=0.0
exceeds_volts=np.where(arr[:]>5)[0]
if len(exceeds_volts)>10:
    raise Exception
arr[arr>5]=5
gmax = 0.2
print(np.nanmean(arr,axis=1))

plt.subplot(1,2,1)
plt.plot(arr[0,:])
plt.plot(arr[1,:])
plt.title('Example Output')
plt.ylabel('Volts')
ticks=[0,.5,1]
plt.xticks([x*expInfo['fs'] for x in ticks],ticks)
plt.show()