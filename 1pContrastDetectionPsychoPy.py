from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
from nidaqmx import stream_writers

import datetime
import random
import pickle
import pandas as pd
import nidaqmx as ni

class ContrastDetectionTask:
    
    def __init__(self):
        #variables for file id 
        base_dir = 'C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/'

        expInfo = {'mouse':'Mfake',
        'date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S'),
        'flicker': True,
        'Depth': '0',
        'monitor_dist': 7,
        'position_1': 0,
        'position_2': 0,
        'is_opto': True,
        }

        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()


        self.alt_stim=False
        self.rand_reward=True
        
        expInfo['I(mA)']= '0'
        expInfo['T(uS)'] = '0'
        expInfo['random_opto']=True
        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']
        
        #stimulus variables
        tf = 2 #temporal frequency
        position = np.array([expInfo['position_1'], expInfo['position_2']])
        sf = .08
        sizes = [0,20]
        intensities = {}
        intensities[0] = [0,0]
        intensities[20] = [10,16,64,100]#[8,32,64,100]#[8,16,32,100]#[4,8,32,100]#[8,16,32,100]#[2,4,8,32]#[2,4,8,32]#[4,8,16,32,100]#[8,16,64,80,90,100]
        expInfo['static']=True
        expInfo['noise'] = False
        self.noise = expInfo['noise']
        #intensities[10] = [2,16,32,64, 100]
        opto_weights = [2,1]

        
        #task variables
        self.random_opto = expInfo['random_opto']
        self.stim_delay = .2 #in s
        self.stim_time = .5 #in s
        self.response_window = 1 # in sq
        self.isimin = 3.8 # in s
        self.isimax = 8 #in s. 2/23/22 moved to 8
        self.grace_time = 1 #in s
        self.water_time = 110 #5/14/22 changed from 125 #5/3 100 #in ms
        self.rand_opto_range = [.2,1]
        tf=2
    
        #monitor variables
        monitor_width = 19.7#22.5 #in cm
        monitor_height = 15#13 #in cm

        
        #initialize
        self.monitor = monitors.Monitor('iPadRetinaApril21', width=monitor_width, distance=expInfo['monitor_dist'])
        self.win = visual.Window(fullscr=True, monitor=self.monitor, units="pix", size=[1600, 1200])
        
        print('generated window')
        FR = self.win.getActualFrameRate()
        expInfo['FR'] = FR 
        expInfo['monitor_height'] = monitor_height
        expInfo['water_time'] = self.water_time
        expInfo['position'] = position
        expInfo['stim_time'] = self.stim_time
        expInfo['sf'] = sf
        expInfo['tf'] = tf
        expInfo['response_window'] = self.response_window
        expInfo['rand_opto_range'] = self.rand_opto_range
        expInfo['stim_delay']=self.stim_delay
        expInfo['fs']=5000
        self.pix_per_deg = self.monitor.getSizePix()[1]/(np.degrees(np.arctan(monitor_height/expInfo['monitor_dist'])))       
        


        self.opto_length_s = (expInfo['stim_time']+ expInfo['response_window'] +
            expInfo['stim_delay'])
        print('opto len s',self.opto_length_s)
        if self.random_opto:
            self.opto_length_s = (expInfo['stim_time']+ expInfo['response_window'] +
            expInfo['stim_delay']+self.rand_opto_range[1])
            
            print(self.opto_length_s,self.rand_opto_range)
            assert self.isimin > self.opto_length_s+self.rand_opto_range[1]
        self.opto_length = int(np.floor(self.opto_length_s * expInfo['fs']))


        self.led_cond_function_key= [self.gen_no_pulse, self.gen_pwm_pulse]


        print('set up some vars')
        
        #create trial conditions
        self.size_int_response = []
        #mult = math.ceil(500/(sum([len(intensities(s)) for s in sizes])*4))
        #print('I think mult should be ', mult)
        for temp in range(100):
            mini_size_int_response = []
            for iholo in range(len(opto_weights)):
                for _ in range(opto_weights[iholo]):
                    for s in sizes:
                        for ins in intensities[s]:
                            
                            mini_size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0, 'opto': iholo})
            random.shuffle(mini_size_int_response)
            
            self.size_int_response += mini_size_int_response
           
        pd.DataFrame(self.size_int_response).to_csv('M:/Hayley/size_int_resp.csv')

        #and some more general variables
        self.phase_increment = tf/FR
        self.stim_on_frames = int(self.stim_time*FR)
        print('conditions genned')
        self.exp_timer = core.Clock()
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.grating = visual.GratingStim(win=self.win, size=10*self.pix_per_deg, pos=position*self.pix_per_deg,
            sf=sf/self.pix_per_deg,units='pix', ori=180+45, mask='circle')

        if self.noise:
            size = round(sizes[1]*self.pix_per_deg)
            self.grating = visual.NoiseStim(
                win=self.win, name='noise',units='pix',

                noiseImage='testImg.jpg', mask='circle',
                            pos=position*self.pix_per_deg, size=(size,size),
                            color=[1,1,1], colorSpace='rgb', 
                            texRes=512, 
                            noiseType='isotropic', noiseElementSize=4, noiseBaseSf=sf/self.pix_per_deg,
                            noiseBW=.5, noiseFractalPower=0,
                            noiseFilterLower=.01/self.pix_per_deg, noiseFilterUpper=.14/self.pix_per_deg,
                            noiseFilterOrder=3.0, noiseClip=2.0,  interpolate=False, depth=-1.0)


        if self.alt_stim:
            self.grating = visual.GratingStim(win=self.win, size=10*self.pix_per_deg, pos=position*self.pix_per_deg,
                    sf=sf/self.pix_per_deg,units='pix', ori=180, mask='circle')
       
        self.intertrial_isi_count=0
        
        #set up the nidaq
        self.lick_daq = ni.Task()
        self.lick_daq.di_channels.add_di_chan('Dev2/Port1/Line0')
        self.lick_daq.start()
        print('daq launched')
        self.water_daq = ni.Task()
        self.water_daq.do_channels.add_do_chan('Dev2/Port1/Line2')

        #lines to master and SI
        self.comm_daq = ni.Task()
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line4') # to SI, stim indicator
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line1') # to master, stim indicator
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line5') # trigger to master
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line2') # trigger to SI

        self.led_daq = ni.Task()
        self.led_daq.ao_channels.add_ao_voltage_chan('Dev2/ao0')


        self.led_daq.timing.cfg_samp_clk_timing(rate=expInfo['fs'],
            sample_mode= ni.constants.AcquisitionType.FINITE, 
            samps_per_chan= self.opto_length)
        self.led_writer = stream_writers.AnalogMultiChannelWriter(self.led_daq.out_stream,
                auto_start=False)
        print('other daqs launched')
        self.fs=expInfo['fs']#TOFO: why here?

        print('other daqs launched')
         #maybe temp, add some display text
        self.text = visual.TextStim(win=self.win, text='ready to go, waiting for keypress', pos = [0,0])
        self.text.draw()
        self.win.flip()
        event.waitKeys()
        self.exp_timer.reset()
        self.exp = data.ExperimentHandler('ContrastDetectionTask','v0',
            dataFileName = self.filename,
            extraInfo = expInfo)
        self.run_blocks()
        
    def run_blocks(self):
        user_quit = False 
        while not user_quit:
            print('makin trials')
            #do in blocks of randomized trials

            self.trials = data.TrialHandler(self.size_int_response, 1, method='sequential')
            self.trials.data.addDataType('Response')
            self.exp.addLoop(self.trials)
            for trial in self.trials:
                if user_quit:
                    break

                user_quit = self.run_trial(trial)
                if not user_quit:
                   user_quit, fa_times, fa_times_abs, led_times_abs = self.run_isi()
                   self.trials.data.add('FATimes',fa_times)
                   self.trials.data.add('FATimesAbs',fa_times_abs)
                   self.trials.data.add('LEDTimesAbs',led_times_abs)
                self.exp.nextEntry()

            self.exp.saveAsWideText(self.filename)
            self.trials.saveAsWideText(self.filename + '_trials')
            #save remote
            self.trials.saveAsWideText('M:/Hayley/PeriOnline/curr_trials.tsv')
            self.water_daq.stop()
            self.lick_daq.stop()
            self.comm_daq.stop()
            self.led_daq.stop()
            self.led_daq.close()
            self.water_daq.close()
            self.lick_daq.close()
            self.comm_daq.close()

    def present_grating(self):
        phase = 0
        for frame in range(self.stim_on_frames):                   
            phase += self.phase_increment
            
            if self.noise:
                if not self.exp.extraInfo['static']:
                    self.grating.updateNoise()
            else:
                if self.exp.extraInfo['static']:
                    self.grating.setPhase(0)
                else:
                    self.grating.setPhase(phase)

            self.grating.draw()
            self.win.flip()


    def gen_pwm_pulse(self):
        arr = np.ones((1,self.opto_length))*5#*self.exp.extraInfo['blue_volts']
        arr[:,-100:]=0.0
        return arr

    def gen_no_pulse(self):
        #TODO: don't regen
        arr = np.zeros((1,self.opto_length))
        return arr

    def run_trial(self, trial):
        trial_still_running = True
        self.trial_timer.reset()
        responded = []
        response_time = np.nan
        user_quit = False
        self.comm_daq.start()
        self.comm_daq.write([False, False, True, True]) #trigger
        self.trials.data.add('StartTime',self.exp_timer.getTime())

        while trial_still_running:

            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':

                    return True
            current_time = self.trial_timer.getTime()
            
            if current_time <= self.stim_delay:
                continue

            elif (current_time >= self.stim_delay and 
                  current_time <=
                    self.stim_time+self.stim_delay-.2):

                print(trial['intensity'], trial['size'])
                self.grating.setContrast(trial['intensity']/100)
                if not self.noise:
                    self.grating.setSize(round(trial['size']*self.pix_per_deg))
                if self.noise:
                    self.grating.buildNoise()
                if trial['intensity'] > 0:
                    self.comm_daq.write([True, True, False, False])
                else:
                    self.comm_daq.write([True, False, False, False])
                self.present_grating()
                self.comm_daq.write([False, False, False, False])

                
                
            elif current_time >= self.stim_time + self.stim_delay:
                self.grating.setContrast(0)
                self.grating.draw()

                responded = self.lick_daq.read()

            if responded:
                if trial['corr_response']:
                    self.deliver_reward()
                
                response_time = current_time
                print(response_time)
                trial_still_running = False
                self.trials.data.add('Response', 1)
                self.trials.data.add('RespTime', response_time)

            elif current_time >= self.stim_delay+self.stim_time+self.response_window:

                trial_still_running = False
                self.trials.data.add('Response', 0)

            self.win.flip()
        
        self.comm_daq.stop()
        return user_quit

    def deliver_reward(self):
        print('delivering reward')
        self.water_daq.start()
        self.water_daq.write(True)
        core.wait(self.water_time/1000)
        self.water_daq.write(False)
        self.water_daq.stop()

    def run_isi(self):
        user_quit = False
        isi = random.uniform(self.isimin,self.isimax)
        rand_opto_on_time = isi-random.uniform(*self.rand_opto_range)
        self.isi_timer.reset()

        #prep led
        led_cond_next_trial = self.trials.getFutureTrial()['opto']
        print(self.trials.getFutureTrial()['opto'], isi, rand_opto_on_time)
        led_output_next_trial = self.led_cond_function_key[led_cond_next_trial]

        false_alarm_times = []
        false_alarm_times_abs = []
        led_on_times_abs = []
        while self.isi_timer.getTime() < isi:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, [],[],[]
            if (self.random_opto and self.isi_timer.getTime() > rand_opto_on_time and
                self.led_daq.is_task_done()):
                print('trying to launch led')
                self.led_daq.stop()
                self.led_writer.write_many_sample(led_output_next_trial())
                self.led_daq.start()
                led_on_times_abs.append(round(core.getTime(),2))
            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                responded = self.lick_daq.read()
                if responded:
                    print('false alarm!')

                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    false_alarm_times_abs.append(round(core.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()
                    #self.text.text = 'false alarm! now restarting ' + str(isi) + ' countdown'
                    #self.text.draw()
                    #self.win.flip()
        return user_quit, false_alarm_times, false_alarm_times_abs, led_on_times_abs

if __name__ == '__main__':
    ContrastDetectionTask()