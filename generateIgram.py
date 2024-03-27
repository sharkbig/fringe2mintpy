#!/bin/env python 
import os, glob
pair=5
slcPattern='./PS_DS/*/*.slc'
inft_folder='interferogram'
ifglist=open('sbas.csv','w')


#################################################
runCoh=open('run_estCoherence.sh','w')
runUnwrap=open('run_unwrap.sh','w')
runIgram=open('run_generateIgram.sh','w')
slc=sorted(glob.glob(slcPattern))
nslc=len(slc)

if not os.path.isdir(inft_folder):
    os.mkdir(inft_folder)

## generate interferogram
for i in range(nslc-1): 
    for j in range(int(pair/2)):
        if i+j+1>= nslc: continue
        master=slc[i]
        slave=slc[i+j+1]

        folder=f'{inft_folder}/{master.split("/")[-2]}_{slave.split("/")[-2 ]}'
        if os.path.exists(folder):
            pass
        else:
            os.mkdir(folder)
            
        intf=f'{folder}/fine.int'
        cor=f'{folder}/fine.cor'
        unw=f'{folder}/fine.unw'

        print(f'imageMath.py -e="a*conj(b)" --a={master} --b={slave} -o {intf} -t CFLOAT',file=runIgram)
        print(f'{master.split("/")[1]}, {slave.split("/")[1]}',file=ifglist)

        print(f'./estCoherence.py -i {intf} -o {cor}',file=runCoh)
        print(f'unwrap.py -i {intf} -c {cor} -u {unw} -m snaphu -s ../reference',file=runUnwrap)