from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime
import random
import nidaqmx as ni

class ContrastDetectionTask:
    
    def __init__(self):
        #variables for file id 
        base_dir = '/home/hbounds/Desktop/'

        expInfo = {'mouse':'Mfake','date': data.getDateStr()}
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()


        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']
        
        self.exp = data.ExperimentHandler('ContrastDetectionTask','v0',
            dataFileName = self.filename,
            extraInfo = expInfo)

        #stimulus variables
        tf = 2 #temporal frequency
        position = [0,0]
        sf = .08
        sizes = [8, 20, 0]
        intensities = {}
        intensities[0] = [0]
        intensities[8] = [2, 6 , 25, 50,
               70, 86 , 100 ]
        intensities[20] = [2, 6 , 12, 25, 50,
               86 , 100 ]
        
        #task variables
        self.stim_delay = .1 #in s
        self.stim_time = .6 #in s
        self.response_window = 1 # in s
        self.isimin = 3 # in s
        self.isimax = 8 #in s
        self.grace_time = 1 #in s
        self.water_time = 50 #in ms
        tf=2
    
        #monitor variables
        monitor_width = 22 #in cm
        monitor_dist = 10 #in cm
        
        #initialize 
        self.monitor = monitors.Monitor('testMonitor', width=monitor_width, distance=monitor_dist)
        self.win = visual.Window(fullscr=True, monitor=self.monitor, units="deg")
        FR = self.win.getActualFrameRate()
        expInfo['FR'] = FR        
        
        
        #create trial conditions
        self.size_int_response = []
        for temp in range(10):
            mini_size_int_response = []
            for _ in range(4):
                for s in sizes:
                    for ins in intensities[s]:
                        mini_size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0})
            random.shuffle(mini_size_int_response)
            self.size_int_response += mini_size_int_response
        #and some more general variables
        self.phase_increment = tf/FR
        self.stim_on_frames = int(self.stim_time*FR)

        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.grating = visual.GratingStim(win=self.win, size=8, pos=position, sf=sf,units='deg')
        
        #set up the nidaq
        self.lick_daq = ni.Task()
        self.lick_daq.di_channels.add_di_chan('Dev2/Port1/Line0')
        self.lick_daq.start()

        self.water_daq = ni.Task()
        self.water_daq.do_channels.add_do_chan('Dev2/Port1/Line2')
        
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
                self.exp.nextEntry()

            self.exp.saveAsWideText(self.filename)
            self.trials.saveAsWideText(self.filename + '_trials')
            self.water_daq.stop()
            self.lick_daq.stop()
            self.water_daq.close()
            self.lick_daq.close()

    def present_grating(self):
        phase = 0
        for frame in range(self.stim_on_frames):                   
            phase += self.phase_increment
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
                    self.stim_time+self.stim_delay-.1):
                print(trial['intensity'], trial['size'])
                self.grating.setContrast(trial['intensity']/100)
                self.grating.setSize(trial['size'])
                self.present_grating()
                
                
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

            elif current_time >= 1.7:

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
        false_alarm_times = []
        while self.isi_timer.getTime() < isi:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, []
            if self.isi_timer.getTime() > self.grace_time: #if we're out of grace period
                #check for a false alarm
                responded = self.lick_daq.read()
                if responded:
                    print('false alarm!')
                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()
        return user_quit, false_alarm_times

if __name__ == '__main__':
    ContrastDetectionTask()