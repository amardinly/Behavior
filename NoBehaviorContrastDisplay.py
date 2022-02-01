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
        base_dir = 'C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/'

        expInfo = {'mouse':'Mfake',
        'date': datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S'),
        'I(mA)': '0',
        'T(uS)': '0',
        'flicker': True,
        'Depth': '0',
        'monitor_dist': 10.0,
        'position_1': 0,
        'position_2': 0,
        'repeats': 5,

        }
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'NoBehContrastDisplay')
        if dlg.OK==False: core.quit()


        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']+'_nobeh_contr_'
        
        self.exp = data.ExperimentHandler('NoBehContrastDisplay','v0',
            dataFileName = self.filename,
            extraInfo = expInfo)

        #stimulus variables
        tf = 2 #temporal frequency
        position = np.array([expInfo['position_1'], expInfo['position_2']])
        sf = .08
        sizes = [0,30]
        intensities = {}
        intensities[0] = [0]
        intensities[30] =  [4,6,32,64]
        #intensities[30] =  [4,8,100]#[8,16,64,80,90,100]#[7,16,32,64,90,100]#[5, 8, 16, 64, 100]#[4,8,16,64,90,100]#[2,8,16,32,64,100]
        #intensities[10] = [2,16,32,64, 100]
        
        #task variables
        self.stim_delay = .2 #in s
        self.stim_time = .5 #in s
        self.isi_length = 3.5
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
        expInfo['position'] = position
        expInfo['stim_time'] = self.stim_time
        expInfo['sf'] = sf
        expInfo['tf'] = tf
        expInfo['isi_length'] = self.isi_length
        self.pix_per_deg = self.monitor.getSizePix()[1]/(np.degrees(np.arctan(monitor_height/expInfo['monitor_dist'])))       
        
        print('set up some vars')
        
        #create trial conditions
        self.size_int_response = []
        #mult = math.ceil(500/(sum([len(intensities(s)) for s in sizes])*4))
        #print('I think mult should be ', mult)
        for _ in range(expInfo['repeats']):
            for s in sizes:
                for ins in intensities[s]:
                    self.size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0})
        random.shuffle(self.size_int_response)
            

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

        #lines to master and SI
        self.comm_daq = ni.Task()
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line4') # to SI, stim indicator
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line1') # to master, stim indicator
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line5') # trigger to master
        self.comm_daq.do_channels.add_do_chan('Dev2/Port0/Line2') # trigger to SI

        print('other daqs launched')
        self.run_blocks()
        
    def run_blocks(self):
        user_quit = False 
        
        print('makin trials')
        #do in blocks of randomized trials

        self.trials = data.TrialHandler(self.size_int_response, 1, method='sequential')
        self.exp.addLoop(self.trials)
        for trial in self.trials:
            if user_quit:
                break
            user_quit = self.run_trial(trial)
            if not user_quit:
                user_quit = self.run_isi()
                #self.trials.data.add('OtherLickTimes', other_licking_times)
            self.exp.nextEntry()

        self.exp.saveAsWideText(self.filename)
        self.trials.saveAsWideText(self.filename + '_contrs')
        self.comm_daq.stop()
        self.comm_daq.close()

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
        self.comm_daq.start()
        self.comm_daq.write([False, False, True, True]) #trigger
        
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

                self.grating.setContrast(trial['intensity']/100)
                self.grating.setSize(trial['size']*self.pix_per_deg)
                if trial['intensity'] > 0:
                    self.comm_daq.write([True, True, False, False])
                else:
                    self.comm_daq.write([True, False, False, False])
                self.present_grating()
                self.comm_daq.write([False, False, False, False])
                
            elif current_time >= self.stim_time + self.stim_delay:
                self.grating.setContrast(0)
                self.grating.draw()
                trial_still_running = False

            self.win.flip()
        
        self.comm_daq.stop()
        return user_quit

    def run_isi(self):
        print('enter isi')
        user_quit = False
        isi = self.isi_length

        self.isi_timer.reset()
        #self.text.text = 'starting ' + str(isi) + ' countdown'
        #self.text.draw()
        self.win.flip()
        while self.isi_timer.getTime() < isi:
            e=event.getKeys()
            if len(e)>0:
                if e[0]=='q':
                    user_quit=True
                    return user_quit
        print('exit isi')
        return user_quit

if __name__ == '__main__':
    ContrastDetectionTask()