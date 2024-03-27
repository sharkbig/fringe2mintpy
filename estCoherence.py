#!/bin/env python 
import numpy as np
import os,glob
import argparse
import isce
import isceobj

def estCoherence(outfile, corfile):
    from mroipac.icu.Icu import Icu

    #Create phase sigma correlation file here
    filtImage = isceobj.createIntImage()
    filtImage.load( outfile + '.xml')
    filtImage.setAccessMode('read')
    filtImage.createImage()

    phsigImage = isceobj.createImage()
    phsigImage.dataType='FLOAT'
    phsigImage.bands = 1
    phsigImage.setWidth(filtImage.getWidth())
    phsigImage.setFilename(corfile)
    phsigImage.setAccessMode('write')
    phsigImage.createImage()

    
    icuObj = Icu(name='sentinel_filter_icu')
    icuObj.configure()
    icuObj.unwrappingFlag = False
    icuObj.useAmplitudeFlag = False
    #icuObj.correlationType = 'NOSLOPE'

    icuObj.icu(intImage = filtImage,  phsigImage=phsigImage)
    phsigImage.renderHdr()

    filtImage.finalizeImage()
    phsigImage.finalizeImage()

def parser():
    args=argparse.ArgumentParser()
    args.add_argument('-i','--int',help="interferogram",dest='int',type=str)
    args.add_argument('-o','--coh',default=None ,dest='coh',type=str,
                      help='output coherence file, default is the replace the suffix with .cor')
    return args

def main():
    args=parser()
    inps=args.parse_args()
    intf=inps.int
    if inps.coh :
        coh=inps.coh
    else:
        coh=intf.replace('.int','.cor')
    estCoherence(intf,coh)

if __name__ == "__main__":
    main()
    
    