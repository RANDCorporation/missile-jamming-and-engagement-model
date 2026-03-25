# -*- coding: utf-8 -*-
"""
Created on Wed May 29 07:05:16 2024

@author: Brien Alkire, RAND, brien@rand.org

This is the primary code entry point where the user can adjust the input
data and run the routines to generate results which are output in a .csv
file and .jpg figures.

"""

import sys   
import brien_mjem as vig
import numpy as np
import matplotlib.pyplot as plt
import math
import os
 
try:
    
    ## TO USE THIS CODE, CREATE AN INPUT FILE (CALLED A RUN MATRIX) WHICH
    ## IS A CSV. EACH ROW IS A DIFFERENT RUN AND EACH COLUMN HAS THE DATA
    ## FOR THAT RUN. SEE "MJEM_RunMatrix_ReportExamples.csv" FOR AN UNCLASS EXAMPLE WITH
    ## THE RIGHT FORMAT. SPECIFY THE FILE NAMES FOR THE INPUT AND OUTPUTS
    ## BELOW, THEN RUN THIS CODE. RESULTS WILL BE WRITTEN TO THE OUTPUT
    ## FILES.
    
    # Filenames for the run matrix of input data, the numerical results, and the figures
    RunMatrixFilename="MJEM_RunMatrix_ReportExamples.csv"    
    ResultsFilename="MJEM_Results_ReportExamples.csv"
    FigFilename="MJEM_Results_ReportExamples.jpg"    
    
    # CLASSIFICATION STRING FOR RESULTS FILE
    classification_str="This worksheet is UNCLASSIFIED."
    
    # Number of samples to use for the plots
    numplotsamples=200 
    
    # Open the run matrix input file, read the first line which
    # has heading columns that we can ignore, but throw an exception
    # if the file can't be opened or is empty.
    fi=open(RunMatrixFilename,"rt")
    if True == fi.closed:
        raise Exception("The run matrix file could not be opened.")    
    s=fi.readline()
    if 0 >= len(s):
        raise Exception("The run matrix file is empty.")   
    
    # Open the file for writing and overwrite any existing file, 
    # write column headings, then close the file
    fo=open(ResultsFilename,"wt")
    if True == fo.closed:
        raise Exception("The results file could not be opened.")
    mystr=classification_str+"\n\n"
    fo.write(mystr)
    print("The following results are being saved to CSV file",ResultsFilename)
    mystr="Case,Description,GPS Jamming Range (km),IFTU Jamming Range (km),RMS Position Error (km),Probability Target is in FOR\n"
    fo.write(mystr)
    print(mystr)
    fo.close()
    if False == fo.closed:
        raise Exception("The results file could not be closed.")
    
    # LOOP THROUGH RUN MATRIX AND RUN EACH CASE
    s=fi.readline()
    while 0< len(s):
        
        # Fetch the data for the next run
        #print(s)
        rundata=s.split(',')
        j=0
        casenumber=rundata[j];j=j+1
        caselabel=rundata[j];j=j+1
        missile_vel_kmps=float(rundata[j]);j=j+1
        slantrange_km=float(rundata[j]);j=j+1
        seeker_acqrange_km=float(rundata[j]);j=j+1
        seeker_for_deg=float(rundata[j]);j=j+1
        tle_rms_km=float(rundata[j]);j=j+1 
        timebetweenmeasurements_s=float(rundata[j]);j=j+1
        iftu_latency_s=float(rundata[j]);j=j+1
        gps_jammer_erp_dBW=float(rundata[j]);j=j+1 
        gps_crpa_psl_dB=float(rundata[j]);j=j+1 
        iftu_jammer_erp_dBW=float(rundata[j]);j=j+1
        iftu_freqhop_gain_dB=float(rundata[j]);j=j+1
        iftu_rx_antennapeakgain_dBi=float(rundata[j]);j=j+1
        iftu_rx_antennapsl_dB=float(rundata[j]);j=j+1
        target_evasivemaneuver_g=float(rundata[j]);j=j+1
        target_evasivemaneuverduration_s=float(rundata[j]);j=j+1
        max_los_km=float(rundata[j]);j=j+1
        gps_rmserror_km=float(rundata[j]);j=j+1
        gps_received_signal_power_dBW=float(rundata[j]);j=j+1
        gps_j2s_threshold_dB=float(rundata[j]);j=j+1
        gps_denied=float(rundata[j]);j=j+1  
        offset_rms_positionerror_km=float(rundata[j]);j=j+1
        iftu_denied=float(rundata[j])
    
        print("Case ",casenumber)
        
        # Create a vignette object with the input data
        vignette=vig.MJEM(
            missile_vel_kmps,
            slantrange_km, 
            seeker_acqrange_km, 
            seeker_for_deg, 
            tle_rms_km, 
            timebetweenmeasurements_s, 
            iftu_latency_s, 
            gps_jammer_erp_dBW, 
            gps_crpa_psl_dB, 
            iftu_jammer_erp_dBW,
            iftu_freqhop_gain_dB,
            iftu_rx_antennapeakgain_dBi,
            iftu_rx_antennapsl_dB,
            target_evasivemaneuver_g,
            target_evasivemaneuverduration_s,
            gps_rmserror_km,
            gps_received_signal_power_dBW,
            gps_j2s_threshold_dB,
            max_los_km,
            offset_rms_positionerror_km,
            gps_denied,
            iftu_denied
            )   
        
        ## CALCULATE MOEs
        jam_range_gps_km, jam_range_iftu_km, rms_pos_err_km, prob_targetinFOR=vignette.get_MOPs()
        
        ## OPEN THE FILE FOR APPENDING AND APPEND MOE RESULTS
        fo=open(ResultsFilename,"at")
        if True == fo.closed:
            raise Exception("The results file could not be opened.")
        mystr=str(casenumber)+","+caselabel+","+str(jam_range_gps_km)+","+str(jam_range_iftu_km)+","+str(rms_pos_err_km)+","+str(prob_targetinFOR)+"\n"
        fo.write(mystr)
        fo.close()
        if False == fo.closed:
            raise Exception("The results file could be be closed.")
        print(mystr)    
        
        ## POSITION ERROR OVER TIME AND DISTANCE
        # Get plot data
        elapsedtime_s,distance_km,pos_error_km=vignette.get_plot_data(numplotsamples)
        
        # PLOT
        # The upper limit for the yaxis so the plot is pretty
        ymax=np.max([rms_pos_err_km,vignette.get_seekergroundsampledistance()/2])*1.1
        
        fig,(ax1)=plt.subplots(1,1)
        # Plot the position error versus elapsed time
        ax1.plot(elapsedtime_s,pos_error_km,
                 color='blue')
        # Plot the time when GPS became jammed
        if 0 == gps_denied:
            xvals=np.array([1,1])*(vignette.slantrange_km-jam_range_gps_km)/vignette.missile_vel_kmps
            yvals=np.array([0,ymax])
            ax1.plot(xvals,yvals,
                 color='red',
                 linestyle='dotted')
        # Plot the time when IFTU became jammed
        if 0 == iftu_denied:
            xvals=np.array([1,1])*(vignette.slantrange_km-jam_range_iftu_km)/vignette.missile_vel_kmps
            yvals=np.array([0,ymax])
            ax1.plot(xvals,yvals,
                 color='red',
                 linestyle='dashed')
        # Plot the time when missile reaches seeker acquisition range
        xvals=np.array([1,1])*(vignette.slantrange_km-seeker_acqrange_km)/vignette.missile_vel_kmps
        yvals=np.array([0,ymax])
        ax1.plot(xvals,yvals,
                 color='red',
                 linestyle='dashdot')
        # Plot half the distance of the seeker FOR
        xvals=np.array([1,1])*vignette.get_TOF2target()
        yvals=np.array([0,vignette.get_seekergroundsampledistance()/2])
        ax1.plot(xvals,yvals,
                 color='orange',
                 linestyle='solid',
                 linewidth=3)
        # Setup axis labels and legend, etc.
        legendtxt=['Position Error']
        if 0 == gps_denied:
            legendtxt=legendtxt+['GPS Jamming Range']
        if 0 == iftu_denied:
            legendtxt=legendtxt+['IFTU Jamming Rnage']
        legendtxt=legendtxt+['Seeker Acquisition Range','Seeker FOR']
        ax1.legend(legendtxt,prop={'size': 10})    
#        if 0 == gps_denied:
#            ax1.legend(['Position Error','GPS Jamming Range','IFTU Jamming Range', 'Seeker Acquisition Range','Seeker FOR'],prop={'size': 10})
#        else:
#            ax1.legend(['Position Error','IFTU Jamming Range', 'Seeker Acquisition Range','Seeker FOR'],prop={'size': 10})
        ax1.set_xlabel("Elapsed Time of Flight (seconds)")
        ax1.set_ylabel("RMS Position Error (km)")
        ax1.grid(axis='both')
        ax1.set_xlim([0,vignette.get_TOF2target()])
        ax1.set_ylim([0,ymax])
        
        # Add a second x-axis showing slant range to target
        ax2 = ax1.twiny()
        ax2.set_xlabel("Range to Target (km)")
        new_tick_locations = np.array([0, 
                                       .25*vignette.get_TOF2target(), 
                                       .5*vignette.get_TOF2target(), 
                                       .75*vignette.get_TOF2target(),                                        
                                       vignette.get_TOF2target()-0.1])

        def x_tick_function(X,vel,maxslant):
            V = maxslant-X*vel
            return ["%.0f" % z for z in V]

        ax2.set_xticks(new_tick_locations)
        ax2.set_xticklabels(x_tick_function(new_tick_locations,missile_vel_kmps,slantrange_km))
        ax2.set_xlim([0,vignette.get_TOF2target()*1.05])  
        ax1.set_xlim([0,vignette.get_TOF2target()*1.05])
        
        # Add a second y-axis showing probability target is in seeker FOR
        ax2=ax1.twinx()
        ax2.set_ylabel("Probability Target is in Seeker FOR")
        new_tick_locations=np.array([0.01,
                                     0.25*ymax,
                                     0.5*ymax,
                                     0.75*ymax,
                                     ymax])
        def y_tick_function(Y,gsd):
            V=np.zeros(len(Y))
            for i in range(0,len(Y)):
                V[i]=100*math.erf(gsd/2/np.sqrt(2)/Y[i])
            return ["%.2f%%" %z for z in V]
         
        ax2.set_yticks(new_tick_locations)
        ax2.set_yticklabels(y_tick_function(new_tick_locations,vignette.get_seekergroundsampledistance()))
        
        ## THE SAVED FIGURES ARE BLANK IF I UNCOMMENT THIS LINE!!!!!
        #plt.show()
 
        # Define the directory and filename
        fig_dir = "Figures"
        myfilename="Case_"+str(casenumber)+"_"+FigFilename        

        # Create the directory if it doesn't exist
        os.makedirs(fig_dir, exist_ok=True)

        # Construct the full path
        fig_path = os.path.join(fig_dir, myfilename)
        
         # Save figure
        plt.savefig(fig_path)
        
        # Read the next line
        s=fi.readline()

    # Exit
    fi.close()
    sys.exit("Exited gracefully.")

except Exception as e:
    print("An error occured. Description:",e)
    
except SystemExit as e:
    print(e)    