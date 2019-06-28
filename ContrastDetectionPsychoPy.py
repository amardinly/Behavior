from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy
import numpy as np
import datetime


class ContrastDetectionTask:
    
    def __init__(self):
        #variables for file id 
        base_dir = '/home/hbounds/Desktop/'

        expInfo = {'mouse':'Mfake','date': data.getDateStr()}
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'Contrast Detection Task')
        if dlg.OK==False: core.quit()


        filename = base_dir + expInfo['date']+'_' + expInfo['mouse'] + '.csv'
        
        exp = data.ExperimentHandler('ContrastDetectionTask','v0',dataFileName = filename)

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
        self.stim_delay = .1
        self.stim_time = .6
        self.response_window = 1
        self.isimin = 1
        self.isimax = 4
        self.grace_time = 1
        tf=2
    
        #monitor variables
        monitor_width = 25 #in cm
        monitor_dist = 20 #in cm
        
        #initialize 
        self.monitor = monitors.Monitor('testMonitor', width=monitor_width, distance=monitor_dist)
        self.win = visual.Window(fullscr=False, monitor=self.monitor, units="deg")
        FR = self.win.getActualFrameRate()
        expInfo['FR'] = FR        
        
        
        #create trial conditions
        self.size_int_response = []
        for s in sizes:
            for ins in intensities[s]:
                self.size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0})
        
        #and some more general variables
        self.phase_increment = tf/FR
        self.stim_on_frames = int(self.stim_time*FR)
        print(FR, self.stim_time, self.stim_on_frames)
        self.trial_timer = core.Clock()
        self.isi_timer = core.Clock()
        self.grating = visual.GratingStim(win=self.win, size=8, pos=position, sf=sf,units='deg')
        
        
        self.run_blocks()
        
    def run_blocks(self):
        user_quit = False
        while not user_quit:
            print('makin trials')
            #do in blocks of randomized trials
            self.trials = data.TrialHandler(self.size_int_response, 4, method='random')
            self.trials.data.addDataType('Response')
            for trial in self.trials:
                print('is a trial')
                if user_quit:
                    break

                user_quit = self.run_trial(trial)

                user_quit, false_alarm_times = self.run_isi()

                self.trials.data.add('FATimes',false_alarm_times)

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
        
        while trial_still_running:

            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':

                    return True
            current_time = self.trial_timer.getTime()
            
            if current_time <= self.stim_delay:
                continue

            elif current_time >= self.stim_delay and current_time <= self.stim_time+self.stim_delay-.1:
                print(self.trials.thisN,  current_time)
                self.grating.setContrast(trial['intensity']/100)
                self.grating.setSize(trial['size'])
                self.present_grating()
                
                
            elif current_time >= self.stim_time + self.stim_delay:
                self.grating.setContrast(0)
                self.grating.draw()

                responded = e

            if responded == 1:
                if trial['corr_response']:
                    deliver_reward(mywin)
                
                response_time = current_time

                trial_still_running = False
                trials.data.add('Response', 1)
                trials.data.add('RespTime', response_time)

            elif current_time >= 1.7:

                trial_still_running = False
                trials.data.add('Response', 0)

            self.win.flip()
        
        
        return user_quit

    def deliver_reward(self):
        print('REWARD')
        pass

    def run_isi(self):
        user_quit = False
        isi = np.random.randint(self.isimin,self.isimax)

        self.isi_timer.reset()
        false_alarm_times = []
        while self.isi_timer.getTime() < isi/1000:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit, []
            if self.isi_timer.getTime() > self.grace_time/1000: #if we're out of grace period
                #check for a false alarm
                responded = e
                if responded:
                    print('false alarm!')
                    false_alarm_times.append(round(self.trial_timer.getTime(),2))
                    isi = np.random.randint(self.isimin,self.isimax)
                    self.isi_timer.reset()
        return user_quit, false_alarm_times
