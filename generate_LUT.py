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
#fix the error where the 8 bit integer thing breaks everything
nearing_limit = np.where(luxes>250)[0]
if len(nearing_limit)>0:
	print('these values are above 250 ', luxes[nearing_limit])
	nearing_limit = nearing_limit.max()
	print('I think this index is the final correct one ', nearing_limit)
	if nearing_limit < len(luxes)-1:
		for idx in range(nearing_limit+1,len(luxes)):
			print('Im correcting value ', luxes[idx], ' which corresponds to intensity ', intensities[idx])
			luxes[idx] = luxes[idx]+256


luxes = (luxes-luxes.min())
luxes = (luxes/luxes.max())*intensities.max()

lut = interp1d(luxes, intensities)(list(range(0,intensities.max()+1))).astype('uint16')

pickle.dump(lut,
                     open('/home/pi/Documents/lut.p', 'wb'))
        
