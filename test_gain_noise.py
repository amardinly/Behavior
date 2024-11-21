from alphaConvolve import alpha_convolve
import nidaqmx as ni
from nidaqmx import stream_writers
import numpy as np
import matplotlib.pyplot as plt

#set parameters for testing
test_voltage = 0.25
test_channel=0
t=5
expInfo={}
expInfo['alphaRise'] = .001
expInfo['alphaDecay'] = .005
expInfo['tEPSG'] = .01
expInfo['firingRate'] = 300 
expInfo['fs'] = 5000 

length = int(np.floor(t/(1/expInfo['fs'])))-1

sq2 = np.ones((1,length))*test_voltage

sq1 = np.zeros((1,length))

if test_channel==0:
    arr=np.vstack([sq2,sq1])
else:
    arr=np.vstack([sq1,sq2])
arr[:,-100:]=0.0
print(arr.max())
print(arr.min())
print(arr.shape)

#open daq
led_daq = ni.Task()
led_daq.ao_channels.add_ao_voltage_chan('Dev1/ao0')
led_daq.ao_channels.add_ao_voltage_chan('Dev1/ao1')
led_daq.timing.cfg_samp_clk_timing(rate=expInfo['fs'],
            sample_mode= ni.constants.AcquisitionType.CONTINUOUS, )
            #samps_per_chan= length)
led_writer = stream_writers.AnalogMultiChannelWriter(led_daq.out_stream,
            auto_start=False)
print(led_daq.is_task_done())
#queue output, wait to finish
led_writer.write_many_sample(arr)
led_daq.start()
print(led_daq.is_task_done())

led_daq.wait_until_done() 
print(led_daq.is_task_done())
led_writer.write_many_sample(arr)
led_daq.start()
print('round2',led_daq.is_task_done())

#clean up
led_daq.stop()
led_daq.close()

gmax = .63
while True:
    try:
        noise = alpha_convolve(gmax,
                expInfo['alphaRise'],expInfo['alphaDecay'],30,expInfo['tEPSG'],
                expInfo['fs'],expInfo['firingRate'])
    except:
        print('max value exceeded, trying a second time and if fails will quit',gmax)
        noise = alpha_convolve(gmax,
                expInfo['alphaRise'],expInfo['alphaDecay'],30,expInfo['tEPSG'],
                expInfo['fs'],expInfo['firingRate'])
    if np.mean(noise) <= test_voltage+.02 and np.mean(noise)>= test_voltage-.02:
        print('found a gmax!, its',gmax, np.mean(noise))
        break
    if np.mean(noise)>= test_voltage+.02:
        print('exceeded mean goal, thats no good',gmax,np.mean(noise))
    gmax+=.02



means=[]
for _ in range(500):
    noise = alpha_convolve(gmax,
                expInfo['alphaRise'],expInfo['alphaDecay'],1.1,expInfo['tEPSG'],
                expInfo['fs'],expInfo['firingRate'])
    means.append(np.mean(noise))
if True:
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


#generate test stimuli
if False:
    for i in range(4):
        noise = alpha_convolve([.5,.7,1,1.3][i],
                expInfo['alphaRise'],expInfo['alphaDecay'],17,expInfo['tEPSG'],
                expInfo['fs'],expInfo['firingRate'])
        plt.subplot(2,2,i+1)
        plt.hist(noise[0,:])
        plt.title(str([.5,.7,1,1.3][i]))
        print('mean',noise.mean(),'95 perc', np.percentile(noise,95),'max',noise.max())
    plt.show()
