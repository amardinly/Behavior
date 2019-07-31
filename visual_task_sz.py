import numpy as np # fundamental package for scientific computing
import time
import tkinter as tk
import PIL as pl
from PIL import ImageTk, Image
import RPi.GPIO as GPIO
import pickle
import scipy.stats as st
from scipy.ndimage import gaussian_filter

def genSinusoid(sz, A, omega, rho, cpp):
    # Generate Sinusoid grating ranging btwn -1 and 1
    # sz: size of generated image (width, height)
    radius = (int(sz[1]/2.0), int(sz[0]/2.0))
    [x, y] = np.meshgrid(range(-radius[0], radius[0]+1), range(-radius[1], radius[1]+1)) # a BUG is fixed in this line
    stimuli = A * np.cos(cpp * omega[0] * x  + cpp *omega[1] * y + rho)
    return stimuli

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.base_size = (480,800)
	#use pickle to load LUT
        with open('/home/pi/Documents/lut.p','rb') as f:
            self.LUT = pickle.load(f)
            self.verbose = False
        self.blank_level = None
        self.size1 = None
        self.scale1 = None
        self.size2 = None
        self.scale2 = None
        self.canvas = tk.Canvas(self, width=self.base_size[1],
                                height=self.base_size[0])
        self.canvas.pack()
        theta = np.pi/4
        omega = [np.cos(theta)/15, np.sin(theta)/15]
        cpp = .425 #cycles per pixel, probably stop hardcoding this 
        #pregen the sinusoids at full contrast, will alter later
        self.sinusoids = [genSinusoid(**{'A':1, 'omega':omega,
                                         'rho':i*np.pi/8,
                                         'sz':self.base_size,
                                         'cpp':cpp}) \
             for i in range(16)]
        

        self.blank = np.zeros(self.base_size, 'uint8')
        self.blank = Image.fromarray(self.blank)
        self.blank = ImageTk.PhotoImage(image=self.blank)

        self.noise = None
                          
        self.start = time.time()
        self.index = 0 #gets reset every time you start 
        #create the image display container
        self.canv_im = self.canvas.create_image(0,0, anchor=tk.NW,
                                                image=self.blank)

        self.do_display = False
        self.last_cb_time = 0
        self.photos_dict = {} #contains photoimages for all possible intensities
        self.photos = [] #contains photoimages actively being displayed
        self.is_init = False
        
    def generate_noise(self, mean_lum, sigma, filt_sigma):
        self.noise = np.random.normal(128, 128*2,
                                      size = self.base_size)
        print(self.noise.min(), self.noise.max())

        self.noise = gaussian_filter(self.noise, 6)
        print(self.noise.min(), self.noise.max())
        self.noise = self.noise - self.noise.min()
        self.noise = self.noise/self.noise.max()
        self.noise = self.noise * 255

        self.noise = self.noise.astype('uint8')
        print(self.noise.min(), self.noise.max())
        self.noise = self.LUT[self.noise]
        print(self.noise.min(), self.noise.max())
        self.noise = Image.fromarray(self.noise)
        self.noise = ImageTk.PhotoImage(image=self.noise)

    def generate_blank(self):
        """ creates a blank image with lum at the currently set self.blank_level """
        self.blank = np.zeros(self.base_size, 'uint8') + self.LUT[self.blank_level]
        self.blank = Image.fromarray(self.blank)
        self.blank = ImageTk.PhotoImage(image=self.blank)

    def create_gratings(self, intensity, scale, size):
        """ create the grating set for a given intensity """
        conv_array = [arr for arr in self.sinusoids]
        conv_array = [np.uint8(arr*int(intensity/2)+128) for arr in conv_array]
        conv_array = [self.LUT[arr] for arr in conv_array]

        if scale is not 100:
            for arr in conv_array:
                change = np.floor(size[0]/2)
                midpts = np.floor(np.asarray(self.base_size)/2)
                arr[0:int(midpts[0]-change),:] = self.LUT[self.blank_level]
                arr[:,0:int(midpts[1]-change)] = self.LUT[self.blank_level]
                arr[int(midpts[0]+change):,:] = self.LUT[self.blank_level]
                arr[:,int(midpts[1]+change):] = self.LUT[self.blank_level]

            
        if intensity==0:
            conv_array = [np.uint8(arr*intensity+self.LUT[self.blank_level]) for arr in self.sinusoids]
        
        images = [Image.fromarray(arr) for arr in conv_array]
        self.photos_dict[(scale, intensity)] = [ImageTk.PhotoImage(image=im) for im in images]


    def stop_grating(self):
        self.do_display = False
        self.nextSize = None
        self.nextIntensity = None

    def update_grating(self):
        """ the method that handles the actual display. It will display whichever photo set is
	currently stored in self.photos. It begins at the one at self.index. Will update by
	calling itself until do_display is set to False, at which point it resets the image
	to the blank
	"""
        if len(self.photos) > 0:
            if self.verbose:
                print(time.time()-self.start)
            self.start = time.time()
            self.photo = self.photos[self.index % (len(self.photos)-1)]
            self.canvas.itemconfig(self.canv_im, image = self.photo)
            self.update()
            self.index += 1
            if self.do_display:
                self.after(10, self.update_grating)
            else:
                if self.verbose:
                    print('stim on for ', time.time()-self.start)
                self.photo = self.blank
                self.photos = []
                self.nextSize = None
                self.nextIntensity = None
                self.canvas.itemconfig(self.canv_im, image = self.photo)
        else:
            print('no photos yet')

    def start_grating(self):
        """ enters the grating display mode, so to speak, by setting index to 0,
	do_display to True, and launching update_grating, which will call itself
	"""
        self.index = 0
        self.do_display = True
        self.start = time.time()
        self.update_grating()

    def stim_pin_callback(self, _):
        """ if the pin is on, thus meaning it was rising, starts the grating display,
        otherwise if its off, meaning it was a falling edge, stops the grating.
	"""
        if self.verbose:
            print('time since callback', time.time() - self.last_cb_time)
        self.last_cb_time = time.time()
        if GPIO.input(27): #if it was a rising callback
            self.start_grating()
        else:
            self.stop_grating()

    def to_pin_callback(self, _):
        print('TIME OUT')
        if GPIO.input(13):
            print(self.noise is None)
            if self.noise is not None:
                self.photo = self.noise
                self.canvas.itemconfig(self.canv_im, image = self.photo)
        else:
            print('but not on')
            self.photo = self.blank
            self.canvas.itemconfig(self.canv_im, image = self.photo)

            

    def init_pin_callback(self, _):
        """change state between is_init, which will cause the receive callback to change.
        In the initiation state, first all session variables, the size, blank level,
        photos dict and intensities and photos are erased. By setting to the initiation state,
        the rec_pin_callback will fill these variables in, instead of setting trialwise variables.
        Once the initiation is completed, based on a falling edge trigger, it will regenerate the
        blank level and new gratings, and then display the new background
        """
        if self.verbose:
            print('init callback')
        if GPIO.input(26):
            print('am doing init')
            self.is_init = True
            self.photos_dict = {}
            self.intensities = []
            self.nextSize = None
            self.nextIntensity = None
            self.photos = []
            self.blank_level = None
            self.size1 = None
            self.size2 = None
            self.scale1 = None
            self.scale2 = None

        else:
            print('end init')
            self.is_init = False
            self.generate_blank()
            self.generate_noise(self.blank_level, self.blank_level,
                                2)
            szes = [self.size1, self.size2]
            scles = [self.scale1, self.scale2]
            [[self.create_gratings(it, scles[k], szes[k]) \
              for it in self.intensities] for k in range(0,2)]
            #set the new blank background
            self.photo = self.blank
            self.canvas.itemconfig(self.canv_im, image = self.photo)
            
    

    def rec_pin_callback(self, _):
        """reads the number sent by the pi, called intensity. If during initiation, uses it to
        assign size, then blank level, and then add to the intensities list, in that order. If
        initiation is complete, will set self.photos to the photo set for that intensity, meaning
        that when stim is activated it will display those photos
        """
        intensity = self.read_bin_pins()
        if self.is_init:
            if self.size1 is None:
                self.scale1=intensity
                print('setting size ', intensity)
                self.size1 = (np.floor(self.base_size[0]*(intensity/100.0)),
                             np.floor(self.base_size[1]*(intensity/100.0)))
            elif self.size2 is None:
                self.scale2=intensity
                print('set size 2 ', intensity)
                self.size2 = (np.floor(self.base_size[0]*(intensity/100.0)),
                             np.floor(self.base_size[1]*(intensity/100.0)))

            elif self.blank_level is None:
                print('setting black ', intensity)
                self.blank_level = intensity
            else:
                print('adding intensity ', intensity)
                self.intensities.append(intensity)
        elif len(self.photos_dict) > 0:
            if self.nextSize is None:
                print('setting next size ', intensity)
                self.nextSize = intensity
            elif self.nextIntensity is None:
                print('setting next int ', intensity)
                self.nextIntensity = intensity
                self.photos = self.photos_dict[(self.nextSize,
                                                self.nextIntensity)]
                self.nextSize = None
                self.nextIntensity = None
            if self.verbose:
                print('intensity trial set ', intensity)
            

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
toPin = 13;
GPIO.setup(stimOnPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(initPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(recPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(toPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#set the binary reading pins
binPins = [j for j in range(24, 16, -1)]
for bp in binPins:
    GPIO.setup(bp, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#to start, lets just set an event callback to display a visual stimulus.

GPIO.add_event_detect(stimOnPin, GPIO.BOTH)
GPIO.add_event_detect(initPin, GPIO.BOTH)
GPIO.add_event_detect(recPin, GPIO.RISING)
GPIO.add_event_detect(toPin, GPIO.BOTH)

GPIO.add_event_callback(stimOnPin, app.stim_pin_callback)
GPIO.add_event_callback(initPin, app.init_pin_callback)
GPIO.add_event_callback(recPin, app.rec_pin_callback)
GPIO.add_event_callback(toPin, app.to_pin_callback)


app.mainloop()
