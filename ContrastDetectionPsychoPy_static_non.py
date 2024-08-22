from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime
import random
import pickle
import pandas as pd
import nidaqmx as ni

class ContrastDetectionTask:
    
    def __init__(self):
        #variables for file id 
        base_dir = 'C:/Users/inctel/Documents/ContrastDetectionTask/'
        expInfo = {'mouse':'Mfake',
        'date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S'),
        'flicker': True,
        'Depth': '0',
        'monitor_dist': 10.47,
        'position_1': 0,
        'position_2': 0,
        }
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()


        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']
        
        self.exp = data.ExperimentHandler('ContrastDetectionTask','v0',
            dataFileName = self.filename,
            extraInfo = expInfo)

        #stimulus variables
        tf = 2 #temporal frequency
        position = np.array([expInfo['position_1'], expInfo['position_2']])
        sf = .08
        sizes = [0,18]
        intensities = {}
        intensities[0] = [0]
        intensities[18] =  [1,3,5,10,35,100]#[4,8,16,32,100]#[8,16,64,80,90,100]#[7,16,32,64,90,100]#[5, 8, 16, 64, 100]#[4,8,16,64,90,100]#[2,8,16,32,64,100]
        #intensities[10] = [2,16,32,64, 100]
        
        #task variables
        self.stim_delay = .2 #in s
        self.stim_time = .5 #in s
        self.response_window = 1 # in s
        self.isimin = 3 # in s
        self.isimax = 9 #in s
        self.grace_time = 1 #in s
        self.water_time = 100#5/3 100 #in ms
        tf=2
    
        #monitor variables
        monitor_width = 19.7#22.5 #in cm
        monitor_height = 15#13 #in cm

        
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
        expInfo['position'] = position
        expInfo['stim_time'] = self.stim_time
        expInfo['sf'] = sf
        expInfo['tf'] = tf
        expInfo['response_window'] = self.response_window
        self.pix_per_deg = self.monitor.getSizePix()[1]/(np.degrees(np.arctan(monitor_height/expInfo['monitor_dist'])))       
        
        print('set up some vars')
        
        #create trial conditions
        self.size_int_response = []
        #mult = math.ceil(500/(sum([len(intensities(s)) for s in sizes])*4))
        #print('I think mult should be ', mult)
        for temp in range(50):
            mini_size_int_response = []
            for _ in range(3):
                for s in sizes:
                    for ins in intensities[s]:
                        for istat in range(2):
                            mini_size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0,'static':istat})
            random.shuffle(mini_size_int_response)
            
            self.size_int_response += mini_size_int_response

        #and some more general variables
        self.phase_increment = tf/FR
        self.stim_on_frames = int(self.stim_time*FR)
        print('conditions genned')
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.grating = visual.GratingStim(win=self.win, size=10*self.pix_per_deg, pos=position*self.pix_per_deg,
            sf=sf/self.pix_per_deg,units='pix', ori=180+45, mask='circle')

        #maybe temp, add some display text
        self.text = visual.TextStim(win=self.win, text='startup', pos = [-550,-450])
        self.intertrial_isi_count=0
        
        #set up the nidaq
        self.lick_daq = ni.Task()
        self.lick_daq.di_channels.add_di_chan('Dev1/Port1/Line0')
        self.lick_daq.start()

        self.water_daq = ni.Task()
        self.water_daq.do_channels.add_do_chan('Dev1/Port1/Line2')

        
        #lines to master and SI
        print('other daqs launched')
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
                    user_quit, false_alarm_times = self.run_isi()
                    self.trials.data.add('FATimes',false_alarm_times)
                    #self.trials.data.add('OtherLickTimes', other_licking_times)
                self.exp.nextEntry()

            self.exp.saveAsWideText(self.filename)
            self.trials.saveAsWideText(self.filename + '_trials')
            self.water_daq.stop()
            self.lick_daq.stop()
            self.water_daq.close()
            self.lick_daq.close()

    def present_grating(self,trial):
        phase = 0
        print(trial['static'],trial['intensity'])
        for frame in range(self.stim_on_frames):  
            if trial['static']==0:                 
                phase += self.phase_increment
            else:
                phase=0
            self.grating.setPhase(phase)
            self.grating.draw()
            self.win.flip()

    def run_trial(self, trial):
        trial_still_running = True
        self.trial_timer.reset()
        responded = []
        response_time = np.nan
        user_quit = False
        
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
                self.grating.setSize(trial['size']*self.pix_per_deg)
                self.present_grating(trial)

                
                
            elif current_time >= self.stim_time + self.stim_delay:
                self.grating.setContrast(0)
                self.grating.draw()

                responded = not self.lick_daq.read()


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
        self.win.flip()
        false_alarm_times = []
        other_licking_times = []
        while self.isi_timer.getTime() < isi:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, []
            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                responded = not self.lick_daq.read() 
                if responded:
                    print('false alarm!')

                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()
                    self.intertrial_isi_count += 1
                    #self.text.text = 'FA! restarting ' + str(isi) + ' countdown. total IT FA: ' + str(self.intertrial_isi_count)
                    #self.text.draw()
                    #self.win.flip()
            #else:
            #    responded = self.lick_daq.read()
            #    if responded:
            #        other_licking_times.append(round(self.trial_timer.getTime(),2))
        print('finishing run isi')
        return user_quit, false_alarm_times    

if __name__ == '__main__':
    ContrastDetectionTask()