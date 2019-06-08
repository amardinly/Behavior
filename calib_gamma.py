import numpy as np # fundamental package for scientific computing
import time
import tkinter as tk
import PIL as pl
from PIL import ImageTk, Image
import RPi.GPIO as GPIO
import pickle

def genSinusoid(sz, A, omega, rho):
    # Generate Sinusoid grating
    # sz: size of generated image (width, height)
    radius = (int(sz[1]/2.0), int(sz[0]/2.0))
    [x, y] = np.meshgrid(range(-radius[0], radius[0]+1), range(-radius[1], radius[1]+1)) # a BUG is fixed in this line

    stimuli = A * np.cos(.425 * omega[0] * x  + .425 *omega[1] * y + rho)
    return stimuli

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.size = (480, 650)
        self.overrideredirect(1)
        self.canvas = tk.Canvas(self, width=self.size[1], height=self.size[0])
        self.canvas.pack()
        start = time.time()
        theta = np.pi/4
        omega = [np.cos(theta)/15, np.sin(theta)/15]
        """pregen the sinusoids at full contrast, will alter later"""
        self.sinusoids = [genSinusoid(**{'A':1, 'omega':omega,
                                         'rho':i*np.pi/4,
                                         'sz':self.size}) \
             for i in range(8)]
        self.photos_dict = {}
        self.intensity_dict={}

        self.blank = np.zeros(self.size, 'uint8') + 0

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

    def create_gratings(self, intensity):
        print('creating grating :', intensity)
        arr=np.zeros(self.size, 'uint8') + intensity
        im = Image.fromarray(arr)
        self.photos_dict[intensity] = ImageTk.PhotoImage(image=im) 

    #I guess make a publicly accessible method that tells it to stop?
    def stop_grating(self):
        self.do_display = False

    
    def update_grating(self):
        if len(self.photos) > 0:
            #print(time.time()-self.start)
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
            self.canvas.itemconfig(self.canv_im, image = self.photos)
        else:
            self.canvas.itemconfig(self.canv_im, image = self.blank)


    def init_pin_callback(self, _):
        """change state between is_init, which will cause the receive callback to changge
        """
        print('init callback')
        if GPIO.input(26):
            print('am doing init')
            self.is_init = True
            self.photos_dict = {}
            self.intensities = []

        else:
            print('end init')
            self.is_init = False
            [self.create_gratings(it) for it in self.intensities]
            

    def rec_pin_callback(self, _):
        if True: #GPIO.input(25):
            intensity = self.read_bin_pins()
            print(intensity)
            if self.is_init:
                print('intensity init callback', intensity)
                self.intensities.append(intensity)
            elif len(self.photos_dict) > 0:
                print('intensity trial set ', intensity)
                self.photos = self.photos_dict[intensity]
                self.prev_intensity = intensity

    def read_bin_pins(self):
        binPins = [j for j in range(24, 16, -1)]
        bin_mult = [1, 2, 4, 8, 16, 32, 64, 64*2]
        numb = 0
        for i, bp in enumerate(binPins):
            numb += GPIO.input(bp)*bin_mult[i]
        return numb

    def rec_lux_pin_callback(self, _):
        print('lux pin call')
        self.intensity_dict[self.prev_intensity] = self.read_bin_pins()
        pickle.dump(self.intensity_dict,
                     open('/home/pi/Documents/gamma.p', 'wb'))
        print(self.intensity_dict)


    
app=SampleApp()
GPIO.setmode(GPIO.BCM)
#set the triggering pins
stimOnPin = 27
initPin = 26;
recPin = 25;
recLuxPin=16
GPIO.setup(stimOnPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(initPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(recPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(recLuxPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#set the binary reading pins
binPins = [j for j in range(24, 16, -1)]
for bp in binPins:
    GPIO.setup(bp, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#to start, lets just set an event callback to display a visual stimulus.

GPIO.add_event_detect(stimOnPin, GPIO.BOTH)
GPIO.add_event_detect(initPin, GPIO.BOTH)
GPIO.add_event_detect(recPin, GPIO.RISING)
GPIO.add_event_detect(recLuxPin, GPIO.RISING)

GPIO.add_event_callback(stimOnPin, app.stim_pin_callback)
GPIO.add_event_callback(initPin, app.init_pin_callback)
GPIO.add_event_callback(recPin, app.rec_pin_callback)
GPIO.add_event_callback(recLuxPin, app.rec_lux_pin_callback)


app.mainloop()
