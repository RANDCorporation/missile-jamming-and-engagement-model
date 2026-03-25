# -*- coding: utf-8 -*-
"""
Created on Wed May 29 07:04:38 2024
@author: Brien Alkire, RAND, brien@rand.org

This code implements a class for modeling an in-flight target update (IFTU).
Member data include the root-mean-square (RMS) target location error resulting
from a measurement, and the elapsed time between measurements.

RMS velocity error is calculated by subtracting the slant range between
target locations and dividing by the elapsed time between measurements.

The RMS position error of the target can be calculated as a function of the
latency between target location measurements and communication of the IFTU.

The math model was developed from scratch. A prototype was implemented in a
spreadsheet and results from this Python code have be verified against the
spreadsheet prototype. All errors are treated as zero-mean Gaussian.

Future variants should add functionality for a full 3-D model where position
and velocity errors are represented as 3x3 covariance matrices.

"""

import numpy as np

##############################################################################
## DEFINE CLASS FOR IFTU ##
class InFlightTargetUpdate:
    """A class to represent an in-flight target update (IFTU)."""
    
    # Get the revision date.
    def get_version(self):
        """ Returns a string with revision information."""
        return "InFlightTargetUpdate revision 20240606."
    
    def __init__(self, tle_rms_km, timebetweenmeasurements_s):
        """This function initializes an IFTU object.
    
    Input Parameters:
        tle_rms_km: the root-mean-square (RMS) target location error (TLE) in kilometers
          at the time the measurement is taken.
        timebetweenmeasurements_s: elapsed time between measurements of 
         target location in seconds.
"""        
        # Validate inputs
        if 0 > tle_rms_km:
            raise ValueError("The target location error tle_rms_km must be non-negative.")
        if 0 >= timebetweenmeasurements_s:
            raise ValueError("The time between measurements timebetweenmeasurements_s must be positive.")
        
        # Instance Variable    
        self.tle_rms_km=tle_rms_km
        self.timebetweenmeasurements_s=timebetweenmeasurements_s
        
    # Calculate RMS velocity error in km per second at time of measurement. 
    # This based calculated by diving the distance between position measurements
    # and dividing by the time between measurements.
    def get_rmsvelocityerror(self):
        return np.sqrt((1/self.timebetweenmeasurements_s)**2*2*self.tle_rms_km**2)
        
    # Calculate RMS position error given the elapsed time since the last update.
    def get_rmspositionerror(self,elapsedtime_s):
        """Given elapsed time in seconds,\
calculate RMS position error in kilometers.

    Input Parameters:
        elapsedtime_s: elapsed time in seconds.
    Output Parameters:
        The output is RMS position error in km."""
        # Validate inputs
        if 0 > elapsedtime_s:
            raise ValueError("Invalid elapsed time, it must be non-negative.")
            
        return np.sqrt(self.tle_rms_km**2+(2*elapsedtime_s)**2*self.get_rmsvelocityerror()**2)
    
