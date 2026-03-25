# -*- coding: utf-8 -*-
"""
Created on Wed May 29 07:04:38 2024
@author:  Brien Alkire, RAND, brien@rand.org

This code implements a class for modeling an inertial navigation system (INS).
Data members include specification for an INS. Member methods provide
measures of performance such as root-mean-square (RMS) position error of a
platform navigating with the INS.

The model is based in-part on the math and models described in:
    
Horton, Mike. “How to Easily Estimate Vehicle Localization Errors from IMU 
Specs.” ANELLO Photonics (blog), March 1, 2023. 
https://medium.com/anello-photonics/how-to-easily-estimate-vehicle-localization-errors-from-imu-specs-31e6174ff065.

The Horton model does not account for error in aligning the INS of the missile
with the INS of the launch platform. We fit a polynomial to results from the
following paper which evaluated a rapid alignment algorithm and tested it
with fighter aircraft:
    
Groves, Paul D., and Jonathan C. Haddock. “An All-Purpose Rapid Transfer Alignment Algorithm Set,” 160–71, 2001. http://www.ion.org/publications/abstract.cfm?jp=p&articleID=119.
   
Another good source for details on INS is:
    
VectorNav. “Inertial Navigation Primer,” 2024. 
https://www.vectornav.com/resources/inertial-navigation-primer.

The Horton model added together error terms. This is not the correct way to 
accumulate error assuming that all error terms are zero-mean Gaussian. Instead,
the variances should be added (not the RMS terms which are 1-sigma).

"""

import numpy as np

## DEFINE CLASS FOR INS ##
class InertialNavigationSystem:
    """A class to represent an inertial navigation system."""
    
    # Get the revision date.
    def get_version(self):
        """ Returns a string with revision information."""
        return "InertialNavigationSystem revision 20240710b."

    def __init__(self, biasinstability_degperhour=0.01, anglerandomwalk_degpersqrthour=0.01):
        """This function initializes an INS object.
    
    Input Parameters:
        biasinstability_degperhour: the bias instability in degrees per hour
        anglerandomwalk_degpersqrthour: the angle random walk in degrees per square-root hour
"""    
        # Validate inputs
        if 0 > biasinstability_degperhour:
            raise ValueError("The bias instability biasinstability_degperhour must be non-negative.")
        if 0 > anglerandomwalk_degpersqrthour:
            raise ValueError("The angle random walk anglerandomwalk_degpersqrthour must be non-negative.")

        # Instance Variable    
        self.biasinstability_degperhour = biasinstability_degperhour
        self.anglerandomwalk_degpersqrthour=anglerandomwalk_degpersqrthour
        
    # Calculated RMS position error given elapsed time and velocity
    def get_rmspositionerror(self,time_s, vel_kmps):
        """Given elapsed time in seconds, and velocity in km per second,\
calculate RMS position error in kilometers.

    Input Parameters:
        time_s: elapsed time in seconds.
        vel_kmps: velocity in kilometers per second.
    Output Parameters:
        The output is RMS position error in km."""
        # Validate inputs
        if 0 > time_s:
            raise ValueError("Elapsed time time_s must be non-negative.")
       
        # Calculate position error due to bias instability
        angle_bias_rad=self.biasinstability_degperhour*np.pi/180*time_s/3600
        #print("Angle bias",angle_bias_rad)
        bias_rms_error=time_s*vel_kmps*np.tan(angle_bias_rad)
        #print("Bias RMS error", bias_rms_error)
        
        # Calculate position error due to angle random walk
        arw=self.anglerandomwalk_degpersqrthour*np.pi/180*np.sqrt(time_s)/np.sqrt(3600)
        arw_rms_error=time_s*vel_kmps*np.tan(arw)
        #print("ARW RMS error", arw_rms_error)
        
        # Calculation position error due to misalignment
        # First set the polynomial coefficients based on a least-squares fit
        # to the data for a 1 deg/hr IMU from (Groves, 2001)
        a=np.array([0.000003125,0.00108631,0.019285714,-0.023809524])
        misalign_rms_error=np.max([0,a[0]*time_s**3+a[1]*time_s**2+a[2]*time_s+a[3]])/1000
        #print("Misalignment RMS error", misalign_rms_error)
                
        return np.sqrt(bias_rms_error**2 + arw_rms_error**2 + misalign_rms_error**2)
    
