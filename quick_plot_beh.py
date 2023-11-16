import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import argparse


parser = argparse.ArgumentParser(description='quickly check behavioral result')
parser.add_argument('mouse', metavar='mouse', type=str, nargs=1,
                    help='mouses')
args = parser.parse_args()
mouse=args.mouse[0]
plt.ion()
#mouse = 'HB122_1'
all_files = glob.glob('C:/Users/miscFrankenRig/Documents/ContrastDetectionTask/*'+mouse+'*_trials.tsv')
all_files.sort()

for file in reversed(all_files):
	df = pd.read_csv(file,
		sep='\t')

	df=df[df.ran==1]

	try:
			df["TrialNumber"] = np.genfromtxt(df.TrialNumber.values)
	except:
		print('trials not fucked up')
	if 'opto' in df.columns:
		df['holo']=df['opto']
	#df=df[(df.TrialNumber<200)&(df.TrialNumber>0)]
	if len(df)<40:
		continue
	try:
		df["Response"] = np.genfromtxt(df.Response.values)
	except:
		print('neat')
	plt.subplot(1,2,1)
	plt.gca().clear()

	
	if 'holo' in df.columns:
		if df.holo.nunique()>1:
			for i in range(df.holo.nunique()):
				intensities = df[df.holo==i].intensity.unique()
				intensities.sort()
				perc_cor=[]
				for intensity in intensities:
					perc_cor.append(len(df[(df.Response==1)&(df.intensity==intensity)&(df.holo==i)])/len(df[(df.intensity==intensity)&(df.holo==i)]))
				print('holoid', i, 'hitrate mean', np.nanmean(perc_cor[1:]))
				plt.plot(intensities+1, perc_cor,marker='o',c=['k','r','b'][i],label=['noholo','holo1','holo2'][i])
			plt.legend()
		else:
			intensities = df.intensity.unique()
			intensities.sort()
			perc_cor = []
			for intensity in intensities:
				perc_cor.append(len(df[(df.Response==1)&(df.intensity==intensity)])/len(df[df.intensity==intensity]))
			plt.plot(intensities+1, perc_cor,marker='o',c='k')
	else:
			perc_cor = []
			for intensity in intensities:
				perc_cor.append(len(df[(df.Response==1)&(df.intensity==intensity)])/len(df[df.intensity==intensity]))
			plt.plot(intensities+1, perc_cor,marker='o',c='k')

	print(file.split('/')[-1].split(mouse)[0])
	print(len(df))
	for holo in df.holo.unique():
		print('hit rate', holo)
		print(round(len(df[(df.Response==1)&(df.intensity>0)&(df.holo==holo)])/len(df[(df.intensity>0)&(df.holo==holo)]),3),
			round(len(df[(df.Response==1)&(df.intensity>0)&(df.intensity<100)&(df.holo==holo)])/len(df[(df.intensity>0)&(df.holo==holo)]),3))
	print('unique intensities', df.intensity.unique())
	print('sizes',df['size'].unique())
	
	
	for i,it in enumerate(intensities):
		plt.text(it+np.log(it+.2)*2,perc_cor[i],str(it), va='top',ha='left')

	plt.xscale('log')
	
	plt.title(file.split("ContrastDetectionTask")[-1].split(mouse)[0])


	plt.subplot(1,2,2)
	plt.gca().clear()
	df=df.set_index('TrialNumber')
	plt.plot(df.Response.rolling(20).mean())
	plt.plot(df[df.intensity==df.intensity.max()].Response.rolling(10).mean())


	plt.xlabel('trials')
	#plt.show(block=False)
	plt.waitforbuttonpress(timeout=400)

plt.close()