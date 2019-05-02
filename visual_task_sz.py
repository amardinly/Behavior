import numpy as np # fundamental package for scientific computing
import time
import tkinter as tk
import PIL as pl
from PIL import ImageTk, Image
import RPi.GPIO as GPIO
import pickle
import scipy.stats as st

def genSinusoid(sz, A, omega, rho):
    # Generate Sinusoid grating
    # sz: size of generated image (width, height)
    radius = (int(sz[1]/2.0), int(sz[0]/2.0))
    [x, y] = np.meshgrid(range(-radius[0], radius[0]+1), range(-radius[1], radius[1]+1)) # a BUG is fixed in this line
    cpp = .425
    stimuli = A * np.cos(cpp * omega[0] * x  + cpp *omega[1] * y + rho)
    return stimuli

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.base_size = (480,656)
        with open('/home/pi/Documents/lut.p','rb') as f:
            self.LUT = pickle.load(f)
        self.blank_level=None
        self.size = None
        self.scale = None
        self.canvas = tk.Canvas(self, width=self.base_size[1],
                                height=self.base_size[0])
        self.canvas.pack()
        start = time.time()
        theta = np.pi/4
        omega = [np.cos(theta)/15, np.sin(theta)/15]
        """pregen the sinusoids at full contrast, will alter later"""
        self.sinusoids = [genSinusoid(**{'A':1, 'omega':omega,
                                         'rho':i*np.pi/8,
                                         'sz':self.base_size}) \
             for i in range(16)]
        
        self.photos_dict = {}

        self.blank = np.zeros(self.base_size, 'uint8') #+ self.blank_level

        self.blank = Image.fromarray(self.blank)
        self.blank = ImageTk.PhotoImage(image=self.blank)
                          
        print(time.time()-start)
        self.start = time.time()
        self.index = 0
        self.canv_im = self.canvas.create_image(0,0, anchor=tk.NW, image=self.blank)

        self.do_display = False
        self.last_cb_time = 0
        self.photos=[]
        self.is_init = False
        

    def generate_blank(self):
        
        self.blank = np.zeros(self.base_size, 'uint8') + self.LUT[self.blank_level]

        self.blank = Image.fromarray(self.blank)
        self.blank = ImageTk.PhotoImage(image=self.blank)

    def gkern(self, kerlen, nsig):
        interval = (2*nsig+1.)/(kernlen)
        x = np.linspace(-nsig-interval/2., nsig+interval/2.,kerlen+1)
        kern1d=np.diff(st.norm.cdf(z))
        kernel_raw = np.sqrt(np.outer(kern1d,kern1d))
        kernel = kernel_raw/kernel_raw.sum()
        return kernel

    def make_gauss(self, gaussDim):
        gaussSigma = gaussDim/3
        x, y = np.meshgrid(np.linspace(-1,1,gaussDim),
                           np.linspace(-1,1,gaussDim))
        gauss = np.exp(-(((x**2)+(y**2)) / (2*gaussSigma**2)))
        gauss = gauss-np.min(gauss)
        gauss = gauss/np.max(gauss)
        add_vert = (self.size[0]-50)/2
        add_horiz = (self.size[1]-50)/2
        gauss = np.pad(gauss, ((add_vert, add_vert), (add_horiz, add_horiz
    
    def create_gratings(self, intensity):
        conv_array = [arr for arr in self.sinusoids]
        
        
        conv_array = [np.uint8(arr*int(intensity/2)+128) for arr in conv_array]
        print(np.mean(self.sinusoids[0]))
        print(np.mean(np.mean(conv_array[0])))
        conv_array = [self.LUT[arr] for arr in conv_array]

        if self.scale is not 100:
            gauss = self.make_gauss(self.size[0])
            for arr in conv_array:
                change = np.floor(self.size[0]/2)
                midpts = np.floor(np.asarray(self.base_size)/2)
                arr[0:int(midpts[0]-change),:] = self.LUT[self.blank_level]
                arr[:,0:int(midpts[1]-change)] = self.LUT[self.blank_level]
                arr[int(midpts[0]+change):,:] = self.LUT[self.blank_level]
                arr[:,int(midpts[1]+change):] = self.LUT[self.blank_level]

            
        if intensity==0:
            conv_array = [np.uint8(arr*intensity+self.LUT[self.blank_level]) for arr in self.sinusoids]
        
        images = [Image.fromarray(arr) for arr in conv_array]
        self.photos_dict[intensity] = [ImageTk.PhotoImage(image=im) for im in images]

    #I guess make a publicly accessible method that tells it to stop?
    def stop_grating(self):
        self.do_display = False

    
    def update_grating(self):
        if len(self.photos) > 0:
            print(time.time()-self.start)
            #astart=time.time()
            self.start = time.time()
            self.photo = self.photos[self.index % (len(self.photos)-1)]
            self.canvas.itemconfig(self.canv_im, image = self.photo)
            #print(time.time()-astart)
            self.update()
            #print(time.time()-astart)
            self.index += 1
            #print(time.time()-self.start)
            if self.do_display:
                self.after(10, self.update_grating)
            else:
                print('stim on for ', time.time()-self.start)
                self.photo = self.blank
                self.canvas.itemconfig(self.canv_im, image = self.photo)
        else:
            print('no photos yet')

    def start_grating(self):
        self.index = 0
        self.do_display = True
        self.start = time.time()
        self.update_grating()
        if len(self.photos)>0:
            print('time to display 1 grate ', time.time()-self.start)

    def stim_pin_callback(self, _):
        print('time since callback', time.time() - self.last_cb_time)
        self.last_cb_time = time.time()
        #for now just hardcode some sillyness
        if GPIO.input(27):
            self.start_grating()
        else:
            self.stop_grating()

    def init_pin_callback(self, _):
        """change state between is_init, which will cause the receive callback to changge
        """
        print('init callback')
        if GPIO.input(26):
            print('am doing init')
            self.is_init = True
            self.photos_dict = {}
            self.intensities = []
            self.blank_level=None
            self.size = None

        else:
            print('end init')
            self.is_init = False
            self.generate_blank()
            [self.create_gratings(it) for it in self.intensities]
            

    def rec_pin_callback(self, _):
        if True: #GPIO.input(25):
            intensity = self.read_bin_pins()
            print(intensity)
            if self.is_init:
                print('intensity init callback', intensity)
                if self.size is None:
                    self.scale=intensity
                    print('setting size')
                    self.size = (np.floor(self.base_size[0]*(intensity/100.0)),
                                 np.floor(self.base_size[1]*(intensity/100.0)))
                elif self.blank_level is None:
                    print('setting black')
                    self.blank_level = intensity
                else:
                    self.intensities.append(intensity)
            elif len(self.photos_dict) > 0:
                print('intensity trial set ', intensity)
                self.photos = self.photos_dict[intensity]

    def read_bin_pins(self):
        binPins = [j for j in range(24, 16, -1)]
        bin_mult = [1, 2, 4, 8, 16, 32, 64, 64*2]
        numb = 0
        for i, bp in enumerate(binPins):
            numb += GPIO.input(bp)*bin_mult[i]
        return numb


    
app=SampleApp()
GPIO.setmode(GPIO.BCM)
#set the triggering pins
stimOnPin = 27
initPin = 26;
recPin = 25;
GPIO.setup(stimOnPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(initPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(recPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#set the binary reading pins
binPins = [j for j in range(24, 16, -1)]
for bp in binPins:
    GPIO.setup(bp, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#to start, lets just set an event callback to display a visual stimulus.

GPIO.add_event_detect(stimOnPin, GPIO.BOTH)
GPIO.add_event_detect(initPin, GPIO.BOTH)
GPIO.add_event_detect(recPin, GPIO.RISING)
GPIO.add_event_callback(stimOnPin, app.stim_pin_callback)
GPIO.add_event_callback(initPin, app.init_pin_callback)
GPIO.add_event_callback(recPin, app.rec_pin_callback)


app.mainloop()
