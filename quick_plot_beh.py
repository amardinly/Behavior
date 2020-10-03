import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob

plt.ion()
mouse = 'HB67_4'
all_files = glob.glob('C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/*'+mouse+'*_trials.tsv')
all_files.sort()
for file in all_files:
	df = pd.read_csv(file,
		sep='\t')
	df=df[df.ran==1]
	if len(df)<50:
		continue
	df["Response"] = np.genfromtxt(df.Response.values)
	perc_cor = []
	intensities = df.intensity.unique()
	intensities.sort()
	for intensity in intensities:
		perc_cor.append(len(df[(df.Response==1)&(df.intensity==intensity)])/len(df[df.intensity==intensity]))

	print(file.split('/')[-1].split(mouse)[0])
	print(len(df))
	print(len(df[(df.Response==1)&(df.intensity>0)])/len(df[df.intensity>0]))
	plt.gca().clear()
	plt.plot(intensities, perc_cor)
	
	plt.title(file.split('/')[-1].split(mouse)[0])
	#plt.show(block=False)
	plt.waitforbuttonpress(timeout=400)

plt.close()