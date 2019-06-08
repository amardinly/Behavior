import pickle
from scipy.interpolate import interp1d
import numpy as np

with open('/home/pi/Documents/gamma.p', 'rb') as f:
    data = pickle.load(f)

intensities = list(data.keys())
intensities.sort()
luxes = [data[i] for i in intensities]

#I didn't cut off non-monotonically increasing parts of the function
#hopefully it still works
luxes = np.asarray(luxes)
intensities = np.asarray(intensities)
luxes = (luxes-luxes.min())
luxes = (luxes/luxes.max())*intensities.max()

lut = interp1d(luxes, intensities)(list(range(0,intensities.max()+1))).astype('uint16')

pickle.dump(lut,
                     open('/home/pi/Documents/lut.p', 'wb'))
        
