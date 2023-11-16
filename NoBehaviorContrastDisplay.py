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
        'flicker': True,
        'is_holo': False,
        'n_holo':2,
        'Depth': '0',
        'monitor_dist': 10.0,
        'position_1': 0,
        'position_2': 0,
        'repeats': 5,

        }
        dlg = gui.DlgFromDict(dictionary=expInfo, title = 'NoBehContrastDisplay')
        if dlg.OK==False: core.quit()


        self.filename = base_dir + expInfo['date']+'_' + expInfo['mouse']+'_nobeh_contr_'
        
        

        #stimulus variables
        tf = 2 #temporal frequency
        position = np.array([expInfo['position_1'], expInfo['position_2']])
        sf = .08
        sizes = [0,20]
        intensities = {}
        intensities[0] = [0]
        #intensities[20]=[32,100]
        intensities[20] =  [16,64,100]
        expInfo['static']=True
        expInfo['noise']=False
        self.noise = expInfo['noise']


        holo_weights = [1]
        if expInfo['is_holo']:
            holo_weights = [1]*expInfo['n_holo']

        
        #task variables
        self.stim_delay = .2 #in s
        self.stim_time = .5 #in s
        self.isi_length = 4
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
        self.size_int_response = []
        #mult = math.ceil(500/(sum([len(intensities(s)) for s in sizes])*4))
        #print('I think mult should be ', mult)
        for temp in range(expInfo['repeats']):
            mini_size_int_response = []
            for iholo in range(len(holo_weights)):
                for _ in range(holo_weights[iholo]):
                    for s in sizes:
                        for ins in intensities[s]:
                            mini_size_int_response.append({'size':s,'intensity':ins,'corr_response':ins>0, 'holo': iholo})
            random.shuffle(mini_size_int_response)
            
            self.size_int_response += mini_size_int_response
           
        pd.DataFrame(self.size_int_response).to_csv('M:/Hayley/size_int_resp.csv')
            

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

        self.text = visual.TextStim(win=self.win, text='ready to go, waiting for keypress', pos = [0,0])
        self.text.draw()
        self.win.flip()
        event.waitKeys()

        self.exp = data.ExperimentHandler('NoBehContrastDisplay','v0',
            dataFileName = self.filename,
            extraInfo = expInfo)

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
            if self.exp.extraInfo['static']:
                self.grating.setPhase(0)
            else:
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
                if not self.noise:
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