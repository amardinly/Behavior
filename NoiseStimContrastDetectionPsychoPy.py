from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime
import random
import nidaqmx as ni
from nidaqmx import stream_writers
from alphaConvolve import alpha_convolve
import pandas as pd

class ContrastDetectionTask:
    
    def __init__(self):
        #variables for file id 
        base_dir = 'C:/Users/inctel/Documents/ContrastDetectionTask/'

        expInfo = {'mouse':'Mfake',
        'date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S'),
        'response_window': .5,
        'red_gain': 1.26,
        'blue_gain': 1.36,
        'red_volts':1.3,
        'blue_volts':1.4,

        }
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()

        
        #stimulus variables
        tf = 2 #temporal frequency
        sf = .08
        sizes = [0,20]
        intensities = {}
        intensities[0] = [0,0]
        intensities[20] = [1,2,3,5,20,100]
        led_conds = ['none','square','noise']
        
        
        #task variables
        self.stim_delay = .2 #in s
        self.stim_time = .5 #in s
        self.response_window = expInfo['response_window']# in s
        self.isimin = 3 # in s
        self.isimax = 8 #in s
        self.grace_time = 1 #in s
        self.water_time = 100 #in ms
    
        #monitor variables
        monitor_width = 19.6 #in cm
        monitor_height = 9.5 #in cm

        #led variables
        
        expInfo['alphaRise'] = .001
        expInfo['alphaDecay'] = .005
        expInfo['tEPSG'] = .01
        expInfo['firingRate'] = 200 
        self.led_cond_function_key= {
            'none': self.gen_no_pulse,
            'square': self.gen_square_pulse,
            'noise': self.gen_synaptic_noise_stims
        }

        print('pre window generation')
        #initialize
        expInfo['monitor_dist']=10.47
        self.monitor = monitors.Monitor('BoxMonitor1', width=monitor_width,
         distance=expInfo['monitor_dist'])
        self.win = visual.Window(fullscr=True, monitor=self.monitor, 
            units="pix")
        
        print('generated window')
        FR = self.win.getActualFrameRate()
        expInfo['FR'] = FR 
        expInfo['monitor_height'] = monitor_height
        expInfo['water_time'] = self.water_time
        expInfo['position'] = np.array([0,0])
        expInfo['stim_time'] = self.stim_time
        

        expInfo['sf'] = sf #spatial frequency of grating
        expInfo['tf'] = tf #temporal frequency of greating
        expInfo['response_window'] = self.response_window
        expInfo['fs'] = 5000
        self.reverse_lick = True #if the lick is represented by low volts
        self.pix_per_deg = (self.monitor.getSizePix()[1]/
            (np.degrees(np.arctan(monitor_height/expInfo['monitor_dist']))))      
        
        print('set up some vars')
        
        #create trial conditions
        self.size_int_response = []
        #mult = math.ceil(500/(sum([len(intensities(s)) for s in sizes])*4))
        #print('I think mult should be ', mult)
        for temp in range(50):
            mini_size_int_response = []
            for _ in range(1): #how many blocks to shuffle in
                for s in sizes:
                    for ins in intensities[s]:
                        for led_cond in led_conds:
                            mini_size_int_response.append({'size':s,'intensity':ins,
                                'corr_response':ins>0,
                                'led_cond': led_cond})
            random.shuffle(mini_size_int_response)
            self.size_int_response += mini_size_int_response
        
        #and some more general variables
        self.phase_increment = tf/FR
        self.stim_on_frames = int(self.stim_time*FR)
        print('conditions genned')
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.grating = visual.GratingStim(win=self.win, size=10*self.pix_per_deg, 
                pos=expInfo['position']*self.pix_per_deg,
            sf=sf/self.pix_per_deg,units='pix', ori=180+45, mask='circle')

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
        print('daq launched')
        self.water_daq = ni.Task()
        self.water_daq.do_channels.add_do_chan('Dev1/Port1/Line2')

        self.led_daq = ni.Task()
        self.led_daq.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        self.led_daq.ao_channels.add_ao_voltage_chan('Dev1/ao1')

        self.led_daq.timing.cfg_samp_clk_timing(rate=expInfo['fs'],
            sample_mode= ni.constants.AcquisitionType.FINITE, 
            samps_per_chan= int(np.floor(expInfo['fs']*(self.stim_time+self.response_window))))
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
            self.trials.data.addDataType('Response')
            self.exp.addLoop(self.trials)
            for trial in self.trials:
                
                if user_quit:
                    break

                user_quit = self.run_trial(trial)
                self.text.text = 'trial number' + str(self.trials.thisTrialN)
                self.text.draw()
                self.win.flip()
                if not user_quit:
                    user_quit, false_alarm_times = self.run_isi()
                    self.trials.data.add('FATimes',false_alarm_times)
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

    def present_grating(self):
        phase = 0
        for frame in range(self.stim_on_frames):                   
            phase += self.phase_increment
            self.grating.setPhase(phase)
            self.grating.draw()
            self.text.draw()
            self.win.flip()

    def temp_gen_sine_stims(self):
        t=self.stim_time+self.response_window
        samples = np.linspace(0, t, int(np.floor(self.fs*t)), endpoint=False)
        f=6 #fundamental frequency
        sine= np.sin(2 * np.pi * f * samples)
        f=2 #fundamental frequency
        sine2= np.sin(2 * np.pi * f * samples)
        arr=np.vstack([(sine+1)*3,(sine2+1)*5])
        #make sure it turns off
        arr[:,-100:]=0.0
        return arr

    def gen_synaptic_noise_stims(self):
        t=self.stim_time+self.response_window
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


    def gen_square_pulse(self):
        #TODO: don't regen
        length = int(np.floor(self.fs*(self.stim_time+self.response_window)))
        sq1 = np.ones(length)*self.exp.extraInfo['blue_volts']
        sq2 = np.ones(length)*self.exp.extraInfo['red_volts']
        arr=np.vstack([sq1,sq2])
        arr[:,-100:]=0.0
        print('sq pulse vals',np.unique(arr))
        return arr

    def gen_no_pulse(self):
        #TODO: don't regen
        length = int(self.fs*(self.stim_time+self.response_window))
        sq1 = np.zeros(length)
        sq2 = np.zeros(length)
        arr=np.vstack([sq1,sq2])
        return arr

    def read_lick(self):
        lick = self.lick_daq.read()
        if self.reverse_lick:
            lick = not lick
        return lick


    def run_trial(self, trial):
        trial_still_running = True
        self.trial_timer.reset()
        responded = False
        response_time = np.nan
        user_quit = False

        #set the led type
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
                self.led_daq.start()

                print(trial['intensity'], trial['size'])
                self.grating.setContrast(trial['intensity']/100)
                self.grating.setSize(trial['size']*self.pix_per_deg)
                self.present_grating()
                
                
            elif current_time >= self.stim_time + self.stim_delay:
                #we are in response window
                self.grating.setContrast(0)
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

            self.text.draw()
            self.win.flip()
        
        self.led_daq.wait_until_done()
        self.led_daq.stop()
        return user_quit

    def deliver_reward(self):
        self.water_daq.start()
        self.water_daq.write(True)
        core.wait(self.water_time/1000)
        self.water_daq.write(False)
        self.water_daq.stop()

    def run_isi(self):
        user_quit = False
        isi = np.random.randint(self.isimin,self.isimax)

        self.isi_timer.reset()
        #self.text.text = 'starting ' + str(isi) + ' countdown'
        #self.text.draw()
        #self.win.flip()
        false_alarm_times = []
        while self.isi_timer.getTime() < isi:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, []
            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                responded = self.read_lick()
                if responded:
                    print('false alarm!')

                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()
                    #self.text.text = 'false alarm! now restarting ' + str(isi) + ' countdown'
                    #self.text.draw()
                    #self.win.flip()
        return user_quit, false_alarm_times

if __name__ == '__main__':
    ContrastDetectionTask()