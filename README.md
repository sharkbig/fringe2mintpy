# fringe2mintpy 


## introduction 
fringe (fine resolution insar using gerenalized eigenvector) is developed by NASA JPL to do the PSDS estimation. 
https://github.com/isce-framework/fringe

Since there's no clear instruction for fringe to do the sbas timeseries estimation, here I write a simple bridge code converting fringe result to another sbas code, Mintpy.

Mintpy is a small baselines timesereis code developed by Yunjun Zhang at Miami University. 
https://github.com/insarlab/MintPy




## Step by step
### data preparation 
Using ISCE stack tools (stackSentinel.py, stackStripmap.py) in **SLC** mode to prepare the coregistrated stack.
*ISCE is another code deeloped by NASA JPL to preprocess InSAR/D-InSAR.

### fringe
Following the instruction from fringe to run the PSDS estimator.
https://github.com/isce-framework/fringe/blob/main/docs/workflows.md

### integratePS
In fringe workflow, instead of running script in the original repo, I modified the script to export SLC stack. 
```bash
./integratePS.py -s coreg_stack/slcs_base.vrt -d adjusted_wrapped_DS \
                 -t Sequential/Datum_connection/EVD/tcorr.bin \
                 -p ampDispersion/ps_pixels 
                 -o PS_DS --stamps
```  

### GenerateIgram and run files
modified path parameter in generateIgram.py (or run by default)

`./generateIgram.py` and three run files, `run_geneateIgram.sh`, `run_estCoherence.sh` and `run_unwrap.sh` is created. 

Run them respectively.

### mintpy 
assign the path of unwrap image, coherence, connect component to the path we just genreate in smallbaselineApp.cfg.
Run `smallbaselineApp.py smallbaselineApp.cfg` 

## FRInGE SBAS mode
Here I made some modification to the sbas code to Network.py for ISCE baseline input. 

```bash
./integratePS.py -s coreg_stack/slcs_base.vrt -d adjusted_wrapped_DS/ \
                 -t Sequential/Datum_connection/EVD/tcorr.bin \
                 -p ampDispersion/ps_pixels -b ../baselines \
                 -o PS_DS --sbas -u snaphu
```
*But the workfllow is not yet tested.*


#### contact info
email: timjunyanchen@gmail.com**