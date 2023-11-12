from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime
import random
import pickle
import pandas as pd
from numpy.random import randint
import nidaqmx as ni

class ContrastDetectionTask:
    
    def __init__(self):
        

        expInfo = {'mouse':'Mfake',
        'date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S'),
        'Depth': '0',
        'monitor_dist': 8,
        'position_1': 0,
        'position_2': 0,
        'n_holo':3,
        'is_holo': False,
        'isi_stim':False,
        #'is_holotrain': False #marshel style contrast ramp
        }
        if not expInfo['is_holo']: expInfo['isi_stim']=False

        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()

        expInfo['flicker']=True
        expInfo['I(mA)']= '0' #old variables about the monitor not used anymore
        expInfo['T(uS)'] = '0'
        expInfo['is_holotrain']=False
        expInfo['rand_reward'] = False
        expInfo['reward_holo'] = False #added these distinctions 8.30.23
        self.alt_stim=False

        base_dir = 'C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/'
        remote_dir = 'M:/Hayley/ContrastDetectionTask/'
        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']
        self.remote_filename = remote_dir + expInfo['date']+'_' + expInfo['mouse']
        
        #stimulus variables
        tf = 2 #temporal frequency
        position = np.array([expInfo['position_1'], expInfo['position_2']])
        sf = .08
        sizes = [0,20]
        intensities = {}
        intensities[0] = [0]
        #intensities[20] = [8,16,100,100,100]
        intensities[20] = [8,16,32,100]#[8,16,32,100,100]#[4,8,16,100]#[10,16,64,100]#8,16,64,100]#[12,16,64,100]#[10,16,64,100]#[10,16,64,100]#[16,32,64,100,100]#[8,16,32,64,100,100]
        #intensities[25] = [20, 32,100,100]
        expInfo['static']=True
        expInfo['noise'] = False
        self.noise = expInfo['noise']
        #intensities[10] = [2,16,32,64, 100]
        holo_weights = [2]
        if expInfo['is_holo']:
            holo_weights = [1]*expInfo['n_holo']
            if expInfo['n_holo']==2:
                holo_weights = [2]*expInfo['n_holo']
            #holo_weights= [2,1]
            #if expInfo['is_holotrain']:
            #        holo_weights=[1,1]
        
        #task variables
        self.stim_delay = .2 #in s
        self.stim_time = .5 #in s
        self.response_window = 1#1 # in s
        expInfo['isi_range'] = [3,9] # in s 2/23/22 moved to 8
        self.timeout_range= [4,9] #currently only used for catch timeout
        self.grace_time = 1 #in s
        self.water_time = 110 #5/14/22 changed from 125 #5/3 100 #in ms
        tf=2

        assert self.response_window<2
        assert self.stim_time<2
    
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
        expInfo['restrict_holo'] = False

        self.pix_per_deg = self.monitor.getSizePix()[1]/(np.degrees(np.arctan(monitor_height/expInfo['monitor_dist'])))       
        
        print('set up some vars')
        
        self.size_int_response = self.populate_trials(expInfo,holo_weights,sizes,intensities)
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
            self.grating = visual.NoiseStim(win=self.win, name='noise',units='pix',noiseImage='testImg.jpg', mask='circle',
                            pos=position*self.pix_per_deg, size=(size,size),color=[1,1,1], colorSpace='rgb', texRes=512, 
                            noiseType='isotropic', noiseElementSize=4, noiseBaseSf=sf/self.pix_per_deg, noiseBW=.5, 
                            noiseFractalPower=0, noiseFilterLower=.01/self.pix_per_deg, noiseFilterUpper=.14/self.pix_per_deg,
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
        print('other daqs launched')

        #maybe temp, add some display text
        #self.text = visual.TextStim(win=self.win, text='ready to go, waiting for keypress', pos = [0,0])
        #self.text.draw()

        self.win.flip()
        e=event.waitKeys()
        if len(e)>0:
            if e[0]!='q':
                self.exp_timer.reset()
                self.exp = data.ExperimentHandler('ContrastDetectionTask','v0',
                    dataFileName = self.filename, extraInfo = expInfo)
                self.run_blocks()
            else:
                self.water_daq.stop()
                self.lick_daq.stop()
                self.comm_daq.stop()
                self.water_daq.close()
                self.lick_daq.close()
                self.comm_daq.close()

        
    def populate_trials(self,expInfo,holo_weights,sizes,intensities):
        #create trial conditions
        size_int_response = []
        #mult = math.ceil(500/(sum([len(intensities(s)) for s in sizes])*4))
        #print('I think mult should be ', mult)
        for temp in range(100):
            mini_size_int_response = []
            for iholo in range(len(holo_weights)):
                for _ in range(holo_weights[iholo]):
                    for s in sizes:
                        for ins in intensities[s]:
                            srp={}
                            if expInfo['is_holotrain']:
                                if iholo>0 and ins==100: continue
                                else:
                                    srp={'size':s,'intensity':ins,'corr_response':((ins>0) or (iholo>0)), 'holo': iholo, 'isi':randint(*expInfo['isi_range'])}
                            elif expInfo['rand_reward']:
                                srp={'size':s,'intensity':ins,'corr_response':((ins>0) or (np.random.binomial(1,.25)>0)), 'holo': iholo, 'isi':randint(*expInfo['isi_range'])}    
                            elif expInfo['reward_holo']:
                                srp={'size':s,'intensity':ins,'corr_response':((ins>0) or (iholo>0)), 'holo': iholo, 'isi':randint(*expInfo['isi_range'])}
                                #(np.random.binomial(1,. 25)>0)), 'holo': iholo})
                            else:
                                if expInfo['restrict_holo']:
                                    if iholo>0 and ins==100: continue
                                srp={'size':s,'intensity':ins,'corr_response':ins>0, 'holo': iholo,  'isi':randint(*expInfo['isi_range'])}
                            mini_size_int_response.append(srp)
                            
            random.shuffle(mini_size_int_response)
            fin_mini_size_int_response=[]
            #add the fake trials after final order is set
            if expInfo['isi_stim']:
                for srp in mini_size_int_response:
                    fin_mini_size_int_response.append(srp)
                    if srp['isi']>6:
                        fin_mini_size_int_response.append({'size':-5,'intensity':-5,'corr_response':False, 'holo': randint(0,expInfo['n_holo']),  'isi':0})
            else: fin_mini_size_int_response=mini_size_int_response
            
            size_int_response += fin_mini_size_int_response
        return size_int_response

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

                if self.exp.extraInfo['isi_stim'] and trial.intensity<0:
                    self.exp.nextEntry() #just skip the trial, and I'll add the lick info based daq info later
                    continue

                user_quit = self.run_trial(trial)
                if not user_quit:
                    user_quit, false_alarm_times, other_licking_times,isi_stim_time = self.run_isi(trial)
                    self.trials.data.add('ISIStimTime',isi_stim_time)
                    self.trials.data.add('FATimes',np.unique(false_alarm_times))
                    self.trials.data.add('OtherLickTimes', np.unique(other_licking_times))
                self.exp.nextEntry()

            self.exp.saveAsWideText(self.filename)
            self.trials.saveAsWideText(self.filename + '_trials')
            #save remote
            self.trials.saveAsWideText('M:/Hayley/PeriOnline/curr_trials.tsv')
            self.water_daq.stop()
            self.lick_daq.stop()
            self.comm_daq.stop()
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

    def run_trial(self, trial):
        if trial['intensity']<0:
            return False
        trial_still_running = True
        self.trial_timer.reset()
        responded = []
        response_time = np.nan
        user_quit = False
        self.comm_daq.start()
        self.comm_daq.write([False, False, True, True]) #trigger
        self.trials.data.add('StartTime',self.exp_timer.getTime())
        lick_recorded = False

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
                else:
                    self.grating.buildNoise()
                if trial['intensity'] > 0:
                    self.comm_daq.write([True, True, False, False])
                else:
                    self.comm_daq.write([True, False, False, False])
                self.present_grating()
                self.comm_daq.write([False, False, False, False])
                
            elif current_time >= self.stim_time + self.stim_delay and current_time<self.stim_delay+self.stim_time+self.response_window:
                self.grating.setContrast(0)
                self.grating.draw()

                responded = self.lick_daq.read()

                if responded and lick_recorded==False:
                    if trial['corr_response']:
                        self.deliver_reward()
                    response_time = current_time
                    lick_recorded=True
                    #trial_still_running = False
                    self.trials.data.add('Response', 1)
                    self.trials.data.add('RespTime', response_time)

            elif current_time >= self.stim_delay+self.stim_time+self.response_window:
                trial_still_running = False
                if lick_recorded==False:
                    self.trials.data.add('Response', 0)

            self.win.flip()
        
        self.comm_daq.stop()
        if trial['corr_response']==False and responded==True:
            user_quit = self.deliver_catch_timeout(user_quit)
        return user_quit

    def deliver_catch_timeout(self, user_quit):
        #added on 3/10/23
        self.isi_timer.reset()
        self.win.flip()
        timeout = np.random.randint(*self.timeout_range)
        while self.isi_timer.getTime()<timeout:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, []
        return user_quit

    def deliver_reward(self):
        print('delivering reward')
        self.water_daq.start()
        self.water_daq.write(True)
        core.wait(self.water_time/1000)
        self.water_daq.write(False)
        self.water_daq.stop()

    def run_isi_stim(self):
        self.comm_daq.start()
        self.comm_daq.write([False, False, True, True]) #trigger
        core.wait(self.stim_delay) #maintain the stim extra trigger
        self.comm_daq.write([True, False, False, False])
        core.wait(.01)
        self.comm_daq.write([False,False,False,False])
        self.comm_daq.stop()


    def run_isi(self,trial):
        user_quit = False
        #isi = np.random.randint(*self.isirange)
        isi = trial['isi']
        self.isi_timer.reset()
        self.win.flip()

        do_isi_stim = self.exp.extraInfo['isi_stim'] and self.trials.getFutureTrial()['intensity']<0

        false_alarm_times = []
        other_licking_times = []
        isi_stim_time=np.nan
        while self.isi_timer.getTime() < isi:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, [], [], isi_stim_time
            responded = self.lick_daq.read()

            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                if responded:
                    print('false alarm! total IT FA: ' + str(self.intertrial_isi_count))
                    #false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(*self.timeout_range)
                    self.isi_timer.reset()
                    self.intertrial_isi_count += 1
                    false_alarm_times.append(round(self.trial_timer.getTime(),1))
                    #self.text.text = 'FA! restarting ' + str(isi) + ' countdown. total IT FA: ' + str(self.intertrial_isi_count)
                    #self.text.draw()
                    #self.win.flip()
            
            else:
                responded = self.lick_daq.read()
                if responded:
                    other_licking_times.append(round(self.trial_timer.getTime(),1))
            if do_isi_stim and (isi-self.isi_timer.getTime())<3: #once there's 3 seconds left, do isi stim, but only once
                isi_stim_time = self.trial_timer.getTime()
                print('running isi stim!')
                self.run_isi_stim()
                do_isi_stim = False
        print('finishing run isi')
        return user_quit, false_alarm_times, other_licking_times,isi_stim_time    

if __name__ == '__main__':
    ContrastDetectionTask()