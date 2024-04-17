import numpy as np
import matplotlib.pyplot as plt
import time

def gen_spiking(t,Fs,fr):
	#generate spike mat for alpha convolve
	# generate poisson train
	nBins = int(np.floor(t/(1/Fs)));
	spikeMat = np.random.rand(1, nBins) < fr*(1/Fs);
	spikeMat = np.where(spikeMat==1)[1]; # extra spike times from binary spikeMat
	return spikeMat


def convolve_spiking(gmax, alphaRise, alphaDecay, t, tEPSG, Fs, spikeMat):
	#version of alpha convolve that takes in spikeMat so you can correlate
	# generate alpha function
	timeBase = np.arange(0,t-1/Fs,1/Fs);

	alphaTimeBase = np.arange(0,tEPSG-1/Fs,1/Fs)#(0:1/Fs:tEPSG-1/Fs);
	term1=(np.exp(-(alphaTimeBase/alphaRise)))
	term2=(np.exp(-(alphaTimeBase/alphaDecay)))
	alphaFunction = gmax*(1-term1)*term2;

	convolvedVector = np.zeros((1,len(timeBase))); 

	# loop to convolve poisson train with alpha function
	for i in range(len(spikeMat)):
	    thisCurrent = np.zeros((1,len(timeBase))); 
	    if spikeMat[i]+len(alphaFunction) >= len(timeBase):
	    	continue
	    thisCurrent[0,spikeMat[i]:(spikeMat[i]+len(alphaFunction))] = alphaFunction;

	    if len(thisCurrent)<=len(convolvedVector):

	        convolvedVector = convolvedVector+thisCurrent;
	#convolvedVector = -1*convolvedVector; #flip sign for dynamic clamp (something wrong with dynamic clamp box)
	convolvedVector[convolvedVector>5.0]=5.0
	return convolvedVector



def alpha_convolve(gmax, alphaRise, alphaDecay, t, tEPSG, Fs, fr):
	# Convolve a poisson spike train vector with an alpha function

	# to generate a simulated EPSG train

	# gmax = peak of unitary EPSG in arbitrary units

	# alphaRise and alphaDecay are rise and decay coefficeints of ESPG in s

	# t = duration of the trial in seconds

	# tEPSG = duration of the EPSG in s

	# Fs = sampling rate in Hz

	# fr = input firing rate to model in Hz


	 

	# generate poisson train
	spikeMat=gen_spiking(t,Fs,fr)
	convolvedVector = convolve_spiking(gmax, alphaRise, alphaDecay, t, tEPSG, Fs, spikeMat)
	
	return convolvedVector