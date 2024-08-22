from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime
import random
import nidaqmx as ni
from nidaqmx import stream_writers
from alphaConvolve import alpha_convolve, gen_spiking, convolve_spiking
import pandas as pd
import matplotlib.pyplot as plt

class ContrastDetectionTask:
    
    def __init__(self):
        #variables for file id 
        base_dir = 'C:/Users/inctel/Documents/ContrastDetectionTask/'

        expInfo = {'mouse':'Mfake',
        'date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S'),
        'response_window': .5,
        'red_gain': 0,
        'blue_gain': 0,
        'red_volts': 0,
        'blue_volts': 0,
        'random_opto': True,
        'bg_contrast': 0,
        'contr_change': False,

        }
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()

        
        #stimulus variables
        tf = 2 #temporal frequency
        sf = .08
        default = int(expInfo['bg_contrast']*100)

        sizes = [20]
        intensities = {}
        #default is the catch trial condition, and should always be here!
        intensities[20] = [default,15,20,25,100]
        led_conds = ['none','square']
        #'correlated_noise'
         
        #task variables
        self.stim_delay = 0 #in s
        self.stim_time = .5 #in s
        self.response_window = expInfo['response_window']# in s
        self.isimin = 3.1 # in s
        self.isimax = 8 #in s
        self.rand_opto_range = [.2,1]
        self.grace_time = 1 #in s
        self.water_time = 120 #in ms
        self.random_opto = expInfo['random_opto']
        self.contr_change = expInfo['contr_change']
        self.bg_contrast = expInfo['bg_contrast']

        #monitor variables
        monitor_width = 19.6 #in cm
        monitor_height = 9.5 #in cm

        #led variables
        
        expInfo['alphaRise'] = .001
        expInfo['alphaDecay'] = .005
        expInfo['tEPSG'] = .01
        expInfo['firingRate'] = 300 
        expInfo['fs'] = 5000
        expInfo['gamma_rate'] = 35 #gamma rate in hz if using gamma stims
        expInfo['blue_delay'] = .002 #in seconds, delay from red to blue if using gamma

        self.led_cond_function_key= {
            'none': self.gen_no_pulse,
            'square': self.gen_square_pulse,
            'noise': self.gen_synaptic_noise_stims,
            'correlated_noise': self.gen_correlated_noise_stims,
            'gamma': self.gen_gamma_stims,
        }


        print('pre window generation')
        
        
        expInfo['monitor_height'] = monitor_height
        expInfo['water_time'] = self.water_time
        expInfo['position'] = np.array([0,0])
        expInfo['stim_time'] = self.stim_time
        expInfo['stim_delay'] = self.stim_delay
        expInfo['isimax'] = self.isimax
        expInfo['isimin'] = self.isimin
        expInfo['rand_opto_range'] = self.rand_opto_range
        

        expInfo['sf'] = sf #spatial frequency of grating
        expInfo['tf'] = tf #temporal frequency of greating
        

        #figure out timing and such with led
        self.opto_length_s = (expInfo['stim_time']+ expInfo['response_window'] +
            expInfo['stim_delay'])
        if self.random_opto:
            self.opto_length_s = (expInfo['stim_time']+ expInfo['response_window'] +
            expInfo['stim_delay']+self.rand_opto_range[1])
            
            print(self.opto_length_s,self.rand_opto_range)
            assert self.isimin > self.opto_length_s+self.rand_opto_range[1]
        self.opto_length = int(np.floor(self.opto_length_s * expInfo['fs']))

        self.reverse_lick = True #if the lick is represented by low volts
        

        print('set up some vars')
       
        #create trial conditions
        #guess a shuffle size to make approx blocks of twenty
        shuffle_n = int(24/(len(intensities[20])*len(led_conds)))
        self.size_int_response = []
        for temp in range(25):
            for back_ori in np.random.permutation(['iso','cross']):
                    mini_size_int_response = []
                    for _ in range(shuffle_n): #how many blocks to shuffle in
                        for s in sizes:
                            for ins in intensities[s]:
                                for led_cond in led_conds:
                                    mini_size_int_response.append({
                                        'size':s,'intensity':ins,
                                        'corr_response':ins>default,
                                        'led_cond': led_cond,
                                        'back_ori':back_ori})
                    random.shuffle(mini_size_int_response)
                    self.size_int_response += mini_size_int_response
        print('shuffle is', shuffle_n,'size of blocks', shuffle_n*len(intensities[20])*len(led_conds))
        core.wait(2)
         #initialize
        expInfo['monitor_dist']=10.47
        monitor = monitors.Monitor('BoxMonitor1', width=monitor_width,
         distance=expInfo['monitor_dist'])
        self.win = visual.Window(fullscr=True, monitor=monitor, 
            units="pix")
        
        print('generated window')
        FR = self.win.getActualFrameRate()
        expInfo['FR'] = FR 
        self.pix_per_deg = (monitor.getSizePix()[1]/
            (np.degrees(np.arctan(monitor_height/expInfo['monitor_dist']))))      

        #and some more general variables
        self.phase_increment = tf/FR
        self.stim_on_frames = int(self.stim_time*FR)
        print('conditions genned')
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.big_grating = visual.GratingStim(win=self.win, size=900, 
                pos=[0,0],
            sf=sf/self.pix_per_deg,units='pix', ori=180+45)
        self.grating = visual.GratingStim(win=self.win, size=10*self.pix_per_deg, 
                pos=expInfo['position']*self.pix_per_deg,
            sf=sf/self.pix_per_deg,units='pix', ori=180+45, mask='circle')
        self.grating.setContrast(0)
        self.big_grating.setContrast(expInfo['bg_contrast'])

        #maybe temp, add some display text
        self.text = visual.TextStim(win=self.win, text='startup', pos = [-250,-150],
            height=10,opacity=.35)
        
        #final setup
        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']
        
        self.exp = data.ExperimentHandler('ContrastDetectionTask','v0',
            dataFileName = self.filename,
            extraInfo = expInfo)

        #set up the nidaq
        self.lick_daq = ni.Task()
        self.lick_daq.di_channels.add_di_chan('Dev1/Port1/Line0')
        self.lick_daq.start()

        self.water_daq = ni.Task()
        self.water_daq.do_channels.add_do_chan('Dev1/Port1/Line2')

        self.led_daq = ni.Task()
        self.led_daq.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        self.led_daq.ao_channels.add_ao_voltage_chan('Dev1/ao1')

        self.led_daq.timing.cfg_samp_clk_timing(rate=expInfo['fs'],
            sample_mode= ni.constants.AcquisitionType.FINITE, 
            samps_per_chan= self.opto_length)
        self.led_writer = stream_writers.AnalogMultiChannelWriter(self.led_daq.out_stream,
            auto_start=False)
        print('other daqs launched')
        self.fs=expInfo['fs']#TOFO: why here?
        self.run_blocks()
        
    def run_blocks(self):
        user_quit = False 
        while not user_quit:
            print('makin trials')
            #do in blocks of randomized trials

            self.trials = data.TrialHandler(self.size_int_response, 1, method='sequential')

            self.exp.addLoop(self.trials)
            for trial in self.trials:
                
                if user_quit:
                    break

                user_quit = self.run_trial(trial)

                self.text.text = 'trial number' + str(self.trials.thisTrialN)
                self.text.draw()
                #self.win.flip()

                if not user_quit:
                    user_quit, fa_times, fa_times_abs, led_times_abs = self.run_isi()
                    self.trials.data.add('FATimes',fa_times)
                    self.trials.data.add('FATimesAbs',fa_times_abs)
                    self.trials.data.add('LEDTimesAbs',led_times_abs)
                self.exp.nextEntry()
            print('broken out')
            self.exp.saveAsWideText(self.filename)
            print('saved exp data')
            self.trials.saveAsWideText(self.filename + '_trials')
            print('saved trial data')
            self.water_daq.stop()
            self.lick_daq.stop()
            self.led_daq.stop()
            self.water_daq.close()
            self.lick_daq.close()
            self.led_daq.close()
    

    def gen_synaptic_noise_stims(self):
        t=self.opto_length_s
        expInfo = self.exp.extraInfo
        red_noise = alpha_convolve(expInfo['red_gain'],
            expInfo['alphaRise'],expInfo['alphaDecay'],t,expInfo['tEPSG'],
            expInfo['fs'],expInfo['firingRate'])
        blue_noise = alpha_convolve(expInfo['blue_gain'],
            expInfo['alphaRise'],expInfo['alphaDecay'],t,expInfo['tEPSG'],
            expInfo['fs'],expInfo['firingRate'])

        arr = np.vstack([blue_noise, red_noise])
        arr[:,-100:]=0.0
        return arr

    def gen_correlated_noise_stims(self):
        t=self.opto_length_s
        expInfo = self.exp.extraInfo
        spikeMat = gen_spiking(t,expInfo['fs'],expInfo['firingRate'])
        red_noise = convolve_spiking(expInfo['red_gain'],
            expInfo['alphaRise'],expInfo['alphaDecay'],t,expInfo['tEPSG'],
            expInfo['fs'],spikeMat)
        blue_noise = convolve_spiking(expInfo['blue_gain'],
            expInfo['alphaRise'],expInfo['alphaDecay'],t,expInfo['tEPSG'],
            expInfo['fs'],spikeMat)

        arr = np.vstack([blue_noise, red_noise])
        arr[:,-100:]=0.0
        return arr


    def gen_square_pulse(self):
        #TODO: don't regen
        sq_blue = np.ones(self.opto_length)*self.exp.extraInfo['blue_volts']
        sq_red = np.ones(self.opto_length)*self.exp.extraInfo['red_volts']
        arr=np.vstack([sq_blue,sq_red])
        arr[:,-100:]=0.0
        print('sq pulse vals',np.unique(arr))
        return arr

    def gen_no_pulse(self):
        #TODO: don't regen
        sq1 = np.zeros(self.opto_length)
        sq2 = np.zeros(self.opto_length)
        arr=np.vstack([sq1,sq2])
        return arr

    def gen_gamma_stims(self):
        Fs=self.exp.extraInfo['fs']
        opto_vec=np.arange(self.opto_length)/Fs
        gamma_rate = self.exp.extraInfo['gamma_rate']

        redGamma = np.abs(np.sin(np.pi*gamma_rate*opto_vec));
        redGamma = (redGamma/np.mean(redGamma))*self.exp.extraInfo['red_volts'];
        blueGamma = np.abs(np.sin(np.pi*gamma_rate*(opto_vec - self.exp.extraInfo['blue_delay'])));
        blueGamma = (blueGamma/np.mean(blueGamma))*self.exp.extraInfo['blue_volts'];
        arr=np.vstack([blueGamma,redGamma])
        arr[:,-100:]=0.0
        exceeds_volts=np.where(arr[:]>5)[0]
        if len(exceeds_volts)>10:
            raise Exception
        arr[arr>5]=5
        return arr

    def present_grating(self):
        phase = 0
        for frame in range(self.stim_on_frames):
            if self.bg_contrast==0:                   
                phase += self.phase_increment
                self.grating.setPhase(phase)
            self.big_grating.draw()
            self.grating.draw()
            self.text.draw()
            self.win.flip()

    def read_lick(self):
        lick = self.lick_daq.read()
        if self.reverse_lick:
            lick = not lick
        return lick

    def deliver_reward(self):
        self.water_daq.start()
        self.water_daq.write(True)
        core.wait(self.water_time/1000)
        self.water_daq.write(False)
        self.water_daq.stop()

    def run_trial(self, trial):
        print('trial', trial['intensity'])
        trial_still_running = True
        self.trial_timer.reset()
        responded = False
        response_time = np.nan
        user_quit = False

        #set the led type - old, before random opto
        if not self.random_opto:
            led_cond_this_trial = trial['led_cond']
            led_output_this_trial = self.led_cond_function_key[led_cond_this_trial]
            self.led_writer.write_many_sample(led_output_this_trial())
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
                #we are in stim showing
                self.trials.data.add('StimTimeAbs',core.getTime()) #log in units since launch
                if not self.random_opto:
                    self.led_daq.start()

                print(trial['intensity'], trial['size'])
                self.grating.setContrast(trial['intensity']/100)
                self.grating.setSize(trial['size']*self.pix_per_deg)
                self.present_grating()
                
                
            elif current_time >= self.stim_time + self.stim_delay:
                #we are in response window
                if self.contr_change:
                    self.grating.setContrast(self.bg_contrast)
                else:
                    self.grating.setContrast(0)
                    self.grating.setSize(0)
                self.grating.draw()

                responded = self.read_lick()


            if responded:
                if trial['corr_response']:
                    self.deliver_reward()
                
                response_time = current_time
                trial_still_running = False
                self.trials.data.add('Response', 1)
                self.trials.data.add('RespTime', response_time)

            elif current_time >= self.stim_delay+self.stim_time+self.response_window:
                trial_still_running = False
                self.trials.data.add('Response', 0)

            
            self.big_grating.draw()
            self.grating.draw()
            self.text.draw()
            self.win.flip()
        if self.trials.getFutureTrial()['back_ori']=='cross':
            self.big_grating.setOri(180-45)
        else:
            self.big_grating.setOri(180+45)
        self.big_grating.draw()
        self.grating.draw()
        self.text.draw()
        self.win.flip()
        self.led_daq.wait_until_done()
        self.led_daq.stop()
        return user_quit

    
    def run_isi(self):
        user_quit = False
        isi = random.uniform(self.isimin,self.isimax)
        rand_opto_on_time = isi-random.uniform(*self.rand_opto_range)
        self.isi_timer.reset()

        #prep led
        led_cond_next_trial = self.trials.getFutureTrial()['led_cond']
        print(self.trials.getFutureTrial()['led_cond'], isi, rand_opto_on_time)
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
                responded = self.read_lick()
                if responded:
                    print('false alarm!')

                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    false_alarm_times_abs.append(round(core.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    rand_opto_on_time = isi-random.uniform(*self.rand_opto_range)
                    self.isi_timer.reset()
                    #self.text.text = 'false alarm! now restarting ' + str(isi) + ' countdown, opto is',led_cond_next_trial
                    #self.text.draw()
                    #self.win.flip()
        return user_quit, false_alarm_times, false_alarm_times_abs, led_on_times_abs

if __name__ == '__main__':
    ContrastDetectionTask()