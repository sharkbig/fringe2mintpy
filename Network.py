import numpy as np
from scipy import sparse
import os
import datetime
import time

class Network(object):
    def __init__(self):
        self.dateList = None
        self.baselineDict = {}
        self.pairsDates = []
    def Baselines_from_txt(self,baselines):
        bptxt=os.listdir(baselines)
        refdate=bptxt[0][:8]
        self.baselineDict[refdate]=0
        for i in bptxt:
            f_bp=os.path.join(baselines,i,i+'.txt')
            secdate=i[9:17]
            bp=[]
            with open(f_bp) as f:
                for ln in  f.readlines():
                    if "Bperp (average)" in ln: 
                        bp.append(float(ln.split(':')[1]))
            self.baselineDict[secdate]=np.average(bp)
        return None 
    
    def computeBaseline(self, refDir, secDir):
        import isce
        import isceobj
        from mroipac.baseline.Baseline import Baseline
        import shelve

        #try:
        #    mdb = shelve.open( os.path.join(refDir, 'data'), flag='r')
        #except:
        with shelve.open( os.path.join(refDir, 'raw'), flag='r') as mdb:
            rFrame = mdb['frame']

        #try:
        #    sdb = shelve.open( os.path.join(secDir, 'data'), flag='r')
        #except:
        with shelve.open( os.path.join(secDir, 'raw'), flag='r') as sdb:
            sFrame = sdb['frame']


        bObj = Baseline()
        bObj.configure()
        bObj.wireInputPort(name='masterFrame', object=rFrame)
        bObj.wireInputPort(name='slaveFrame', object=sFrame)

        bObj.baseline()

        print('Baseline at top/bottom: %f %f'%(bObj.pBaselineTop,bObj.pBaselineBottom))

        avgBaseline = (bObj.pBaselineTop + bObj.pBaselineBottom) / 2.0

        return avgBaseline

    def get_baselineDict(self, dataDir):
        refDate = self.dateList[0]
        refDir = os.path.join(dataDir, refDate)
        self.baselineDict[refDate] = 0.0
        for d in self.dateList[1:]:
            secDir = os.path.join(dataDir, d)
            baseline = self.computeBaseline(refDir, secDir)
            self.baselineDict[d] = baseline

    def geometrical_coherence(self, rangeSpacing, theta, wvl, r):

        numDates = len(self.dateList)
        coh = np.zeros((numDates, numDates))

        for i in range(numDates - 1):
            for j in range(i+1,numDates):

                B = np.abs(self.baselineDict[self.dateList[j]] - 
                            self.baselineDict[self.dateList[i]])

                corr = 1.0 - 2*B*rangeSpacing*((np.cos(theta))**2)/wvl/r
                if corr<=0.0:
                    corr = 0.001
                coh[i,j] = corr

        return coh

    def min_span_tree(self, coh, n = 1):
        self.pairsDates = []

        for i in range(n):
            weightMat = 1.0/coh
            mstMat = sparse.csgraph.minimum_spanning_tree(weightMat)

            # Convert MST index matrix into date12 list
            [s_idx_list, m_idx_list] = [date_idx_array.tolist()
                                for date_idx_array in sparse.find(mstMat)[0:2]]

            for i in range(len(m_idx_list)):
                idx = sorted([m_idx_list[i], s_idx_list[i]])
                coh[idx[0],idx[1]] = 0.001
                date12 = self.dateList[idx[0]] + '-' + self.dateList[idx[1]]
                if date12 not in self.pairsDates:
                    #print(date12)
                    self.pairsDates.append(date12)
    def computeTimeDelta(self, date1, date2):
        datefmt='%Y%m%d'
        _date1 = datetime.datetime.strptime(date1, datefmt)
        _date2 = datetime.datetime.strptime(date2, datefmt)
        tempBp= (_date1-_date2).days
        return abs(tempBp)
    

    def small_baseline(self, timeThreshold = 1000, baselineThreshold = 1000):
        self.pairsDates = []
        print('set to default temporal baseline threshold:',timeThreshold)
        print('set to default Bperp threshold:',baselineThreshold)

        pair_list_csv=open('sb_pairs.csv','w')
        bp_list_csv=open('bp_pairs.csv','w')
        for i in range(0, len(self.dateList)):
            master_date = self.dateList[i]
            master_baseline= self.baselineDict[master_date]
            for j in range(i+1, len(self.dateList)):
                slave_date=self.dateList[j]
                slave_baseline= self.baselineDict[slave_date]

                if abs(slave_baseline-master_baseline) < baselineThreshold and \
                    self.computeTimeDelta(master_date,slave_date) < timeThreshold:
                    date12 = master_date + '-' + slave_date
                    self.pairsDates.append(date12)
                    print(master_date,slave_date,sep=',',file=pair_list_csv)
                    print(master_baseline,slave_baseline,sep=',',file=bp_list_csv)
        return None

    def single_master(self,mstIx=0):
        
        master_date = self.dateList[mstIx]
        self.pairsDates = []
        
        for i in range(1, len(self.dateList)):
            date12 = master_date + '-' + self.dateList[i]
            self.pairsDates.append(date12)

        return None

    def plot_network(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt

        datefmt='%Y%m%d'
        fig1 = plt.figure(1)
        ax1=fig1.add_subplot(111)
        ax1.cla()

        for pair in self.pairsDates:
            print(pair)
            d0 = pair.split("-")[0]
            d1 = pair.split("-")[1]
            t0 = datetime.datetime.strptime(d0, datefmt)
            t1 = datetime.datetime.strptime(d1, datefmt)
            b0 = self.baselineDict[d0]
            b1 = self.baselineDict[d1]
            ax1.plot([t0,t1], [b0, b1],
                 '-ko',lw=1, ms=4, alpha=0.7, mfc='r')


        plt.title('Baseline plot')
        plt.xlabel('Time')
        plt.ylabel('Perp. Baseline')
        plt.tight_layout()

        plt.savefig("Pairs.png")




