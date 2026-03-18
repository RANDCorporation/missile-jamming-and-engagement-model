# -*- coding: utf-8 -*-
"""
Created on Wed May 29 07:04:38 2024

@author: Brien Alkire, brien@rand.org
"""

import numpy as np
import brien_iftu as iftu
import brien_ins as ins
import math

##########################################################################################
## DEFINE CLASS FOR MISSILE IFTU VIGNETTE ##

class MJEM:
    """A class to represent a missile jamming vignette."""

    # Get the revision date.
    def get_version(self):
        """ Returns a string with revision information."""
        return "MJEM revision 20240822."

    def __init__(self,
                 missile_vel_kmps = 5*0.33146, 
                 slantrange_km = 1000, 
                 seeker_acqrange_km=100, 
                 seeker_for_deg=10, 
                 tle_rms_km = 0.1, 
                 timebetweenmeasurements_s = 100, 
                 iftu_latency_s=100, 
                 gps_jammer_erp_dBW=45, 
                 gps_crpa_psl_dB=12, 
                 iftu_jammer_erp_dBW=45,
                 iftu_freqhop_gain_dB=12,
                 iftu_rx_antennapeakgain_dBi=12,
                 iftu_rx_antennapsl_dB=12,
                 target_evasivemaneuver_g=0.5,
                 target_evasivemaneuverduration_s=10,
                 gps_rmserror_km = 0.0102,
                 gps_received_signal_power_dBW=-160,
                 gps_j2s_threshold_dB=54,
                 max_los_km=555.2268,
                 offset_rms_positionerror_km = 0,
                 gps_denied=False,
                 iftu_denied=False
                 ):
        """This function initializes a vignette object.
    
    Input Parameters:
                 missile_vel_kmps: velocity of missile in km per second 
                 slantrange_km: slant range of shooter to target in km
                 seeker_acqrange_km: missile seeker target acquisition range in km
                 seeker_for_deg: missile seeker field of regard in degress
                 tle_rms_km: root-mean-square target location error of IFTU when measurement is collected in km
                 timebetweenmeasurements_s: time between target location measurements in seconds
                 iftu_latency_s: time latency between target location measurement and when IFTU is received, in seconds
                 gps_jammer_erp_dBW: emitted radiated power of GPS jammer in dBW
                 gps_crpa_psl_dB: peak-to-sidelobe level of CRPA antenna on GPS receiver in dB
                 iftu_jammer_erp_dBW: ERP of of the IFTU jammer in dBW (matched bandwidth)
                 iftu_freqhop_gain_dB: frequency hoping gain of IFTU receiver in dB
                 iftu_rx_antennapeakgain_dBi: IFTU receiver antenna peak gain in dBi
                 iftu_rx_antennapsl_dB: peak-to-sidelobe level of IFTU receiver antenna in dB
                 target_evasivemaneuver_g: g-force of the target's evasive maneuver
                 target_evasivemaneuverduration_s: duration of the target's evasive maneuver in seconds
                 gps_rmserror_km: RMS position error of the GPS receiver in km
                 gps_received_signal_power_dBW: average power of the GPS received signal in dBW
                 gps_j2s_threshold_dB: the jammer-to-signal power ratio for jamming in track mode in dB
                 max_los_km: maximum line-of-sight slant range in km for jamming (altitude dependent)
                 offset_rms_positionerror_km: a fixed additional position error that can be added, useful for modeling GPS denial
                 gps_denied: True if GPS is completely denied and otherwise False (default)
                 iftu_denied: True if IFTU is complete denied and other False (default)
                 '

"""        
        ## Initialize member data
        self.missile_vel_kmps = missile_vel_kmps
        self.slantrange_km = slantrange_km
        self.seeker_acqrange_km=seeker_acqrange_km
        self.seeker_for_deg=seeker_for_deg
        self.tle_rms_km = tle_rms_km
        self.timebetweenmeasurements_s = timebetweenmeasurements_s
        self.iftu_latency_s= iftu_latency_s
        self.gps_jammer_erp_dBW=gps_jammer_erp_dBW
        self.gps_crpa_psl_dB=gps_crpa_psl_dB
        self.iftu_jammer_erp_dBW=iftu_jammer_erp_dBW
        self.iftu_freqhop_gain_dB=iftu_freqhop_gain_dB
        self.iftu_rx_antennapeakgain_dBi=iftu_rx_antennapeakgain_dBi
        self.iftu_rx_antennapsl_dB=iftu_rx_antennapsl_dB
        self.target_evasivemaneuver_g=target_evasivemaneuver_g
        self.target_evasivemaneuverduration_s=target_evasivemaneuverduration_s
        self.gps_rmserror_km = gps_rmserror_km
        self.gps_received_signal_power_dBW=gps_received_signal_power_dBW
        self.gps_j2s_threshold_dB=gps_j2s_threshold_dB
        self.max_los_km=max_los_km
        self.offset_rms_positionerror_km=offset_rms_positionerror_km
        self.gps_denied=gps_denied
        self.iftu_denied=iftu_denied
        
        ## Initialize member IFTU
        self.iftu = iftu.InFlightTargetUpdate(
            self.tle_rms_km, 
            self.timebetweenmeasurements_s)
        
        ## Initialize member INS using default values
        self.ins=ins.InertialNavigationSystem()
        
        ## Other data members
        self.gps_wavelength_m=3e8/1.227e9 # Wavelength of the L-2 GPS signal to use for jamming calcs
        self.gps_polarizationmismatch_dB = 4.4 # A parameter from Barker et al used in GPS jamming calcs
        
        
        self.iftu_wavelength_m=3e8/2.5e9 # Wavelength of the IFTU signal to use for jamming calcs
        self.iftu_tx2rxrange_km=800 # This is based on a Starlink LEO satellite at 550 km with 43 deg off nadir/43 deg grazing angle
        self.iftu_j2s_threshold_dB=0 # J/S threshold not including freq hop gain 
        self.iftu_tx_erp_dBW=29.33 # Based on 10 Watts RF and a 0.5 meter antenna

    # Get the rms position error due to the target evasive maneuver in km
    def get_rmserror_maneuver(self):
        return self.target_evasivemaneuver_g*9.8/2*self.target_evasivemaneuverduration_s**2/1000       
        
    # Get the ground sample distance of seeker FOR at acquisition range in km
    def get_seekergroundsampledistance(self):
        return self.seeker_acqrange_km*np.tan(self.seeker_for_deg*np.pi/180)       
        
    # Get the maximum GPS jamming range in km
    def get_maxgpsjammingrange(self):
        return np.min([self.slantrange_km,self.max_los_km,self.gps_wavelength_m/(4*np.pi)*10**((-1/20)*(self.gps_j2s_threshold_dB+self.gps_received_signal_power_dBW+self.gps_crpa_psl_dB-(self.gps_jammer_erp_dBW-self.gps_polarizationmismatch_dB)))/1000])      
        
    # Get the maximum IFTU jamming range in km
    def get_maxiftujammingrange(self):
        return np.min([self.slantrange_km,self.max_los_km,self.iftu_tx2rxrange_km*10**((-1/20)*(self.iftu_j2s_threshold_dB+(self.iftu_tx_erp_dBW-(self.iftu_jammer_erp_dBW-self.iftu_freqhop_gain_dB))+self.iftu_rx_antennapsl_dB))])

    # Get the time of flight (TOF) to the target in seconds
    def get_TOF2target(self):
        return self.slantrange_km/self.missile_vel_kmps
    
    # Get the time of flight (TOF) to seeker acquisition range in seconds
    def get_TOF2acquisition(self):
        return np.max([0,(self.slantrange_km-self.seeker_acqrange_km)/self.missile_vel_kmps])
    
    # Get the total duration of time that GPS is jammed in seconds
    def get_durationtimegpsjammed(self):
        return np.max([0,(self.get_maxgpsjammingrange()-self.seeker_acqrange_km)/self.missile_vel_kmps])

    # Get the total duration of time that IFTU is jammed in seconds
    def get_durationtimeiftujammed(self):
        if True == self.iftu_denied:
            tau=self.get_TOF2acquisition()
        else:
            tau=np.max([0,(self.get_maxiftujammingrange()-self.seeker_acqrange_km)/self.missile_vel_kmps])
        return tau

    # Get the measures of performance for the vignette
    def get_MOPs(self):
        """This function calculates and returns measures of performance (MOPs)
for the vignette.
    
    Input Parameters:
                 None.
    Output Parameters:
        The output is a 4-tuple from left-to-right:
            jam_range_gps_km: the range from target at which GPS is jammed in km.
            jam_range_iftu_km: the range from target at which IFTUs are jammed in km.
            rms_pos_err_km: the total RMS position error in km of the missile when it reaches seeker acquisition range.
            prob_targetinFOR: the probability that the target is within the missile FOR when it reaches seeker acquisition range.
"""        
        jam_range_gps_km=0
        jam_range_iftu_km=0
        rms_pos_err_km=0
        prob_targetinFOR=0
        
        ## CALCULATE THE JAMMING RANGES
        jam_range_gps_km=self.get_maxgpsjammingrange()
        jam_range_iftu_km=self.get_maxiftujammingrange()
        
        ## CALCULATE THE EXACT TIME THAT IFTU BECOMES JAMMED
        if True == self.iftu_denied:
            time_iftu_becomes_jammed_s=0
        else:
            time_iftu_becomes_jammed_s=np.max([0,self.get_TOF2acquisition()-self.get_durationtimeiftujammed()])
        #print("Time IFTU becomes jammed is ",time_iftu_becomes_jammed_s)
        
        ## CALCULATE TIME BETWEEN IFTU BECOMING JAMMED AND LAST UPDATE RECEIVED
        iftu_skate_duration_s=time_iftu_becomes_jammed_s % self.timebetweenmeasurements_s
        #print("IFTU Skate Time is",iftu_skate_duration_s)
        
        ## CALCULATE THE DURATION OF TIME THAT GPS AND IFTU ARE JAMMED
        if True == self.gps_denied:
            duration_gps_denied_s=self.get_TOF2acquisition()
        else:
            duration_gps_denied_s=self.get_durationtimegpsjammed()
        
        duration_iftu_denied_s=self.get_durationtimeiftujammed()+iftu_skate_duration_s
        
        ## CALCULATE THE RMS POSITION ERROR BUDGET
        rms_pos_err_km=np.sqrt(
            self.get_rmserror_maneuver()**2 +
            self.gps_rmserror_km**2 + 
            self.iftu.get_rmspositionerror(duration_iftu_denied_s+self.iftu_latency_s)**2 + 
            self.ins.get_rmspositionerror(duration_gps_denied_s,self.missile_vel_kmps)**2 +
            self.offset_rms_positionerror_km**2)
        
        ## CALCULATE PROBABILITY TARGET IS WITHIN SEEKER FOR
        prob_targetinFOR=math.erf(self.get_seekergroundsampledistance()/2/np.sqrt(2)/rms_pos_err_km)
        
        return jam_range_gps_km, jam_range_iftu_km, rms_pos_err_km, prob_targetinFOR

    # Get data for plotting the position error over time and distance
    def get_plot_data(self,n):
        """This function returns data for plotting position error over time and
distance.
    
    Input Parameters:
                 n: the number of data points for the plot.
    Output Parameters:
        The output is a 3-tuple from left-to-right:
            elapsedtime_s: an n-vector with elapsed time since launch in seconds.
            distanceflown_km: an n-vector of distance flown since launch in km
            pos_error_km: an n-vector of RMS position errors for the missile over time and distance.
"""
        # Create an n-vector of evenly spaced time samples
        elapsedtime_s=np.linspace(0,(self.slantrange_km-self.seeker_acqrange_km)/self.missile_vel_kmps,num=n)
        
        # Create an n-vector of evenly spaced distance samples
        distanceflown_km=np.linspace(0,(self.slantrange_km-self.seeker_acqrange_km),num=n)
        
        # Create n-vectors of distance to target and distance to acquisition range for intermediate calcs
        distance2target_km = self.slantrange_km-distanceflown_km
        distance2acq_km = self.slantrange_km-self.seeker_acqrange_km-distanceflown_km
        
        # Initialize position error vector
        pos_error_km=np.linspace(0,0,n)
        
        # Loop through samples and calculate error budget
        time_gps_isjammed_s=0
        isgpsjammed=False
        time_iftu_isjammed_s=0
        isiftujammed=False
        timeoflastiftu_s=0
        for i in range(0,n):

            # GPS error term
            gps_err=self.gps_rmserror_km
            
            #Evasive maneuver error term
            if 0 < distance2acq_km[i]:
                evasive_err=0
            else:
                evasive_err=self.get_rmserror_maneuver()
            
            # INS error term
            if False == self.gps_denied and self.get_maxgpsjammingrange() < distance2target_km[i]:
                ins_err=0
            else:
                # Log the time that GPS became jammed
                if False == isgpsjammed:
                    time_gps_isjammed_s=elapsedtime_s[i]
                    isgpsjammed=True
                ins_err=self.ins.get_rmspositionerror(elapsedtime_s[i]-time_gps_isjammed_s, self.missile_vel_kmps)
                
            # IFTU error term
            if True == self.iftu_denied:
                timeoflastiftu_s=0
                iftu_err=self.iftu.get_rmspositionerror((elapsedtime_s[i]-timeoflastiftu_s)+self.iftu_latency_s)                
            elif self.get_maxiftujammingrange() < distance2target_km[i]:
                timeoflastiftu_s=elapsedtime_s[i]-elapsedtime_s[i]% self.iftu.timebetweenmeasurements_s
                iftu_err=self.iftu.get_rmspositionerror((elapsedtime_s[i]-timeoflastiftu_s)+self.iftu_latency_s)
            else:
                # Log the time that IFTU became jammed
                if False == isiftujammed:
                    time_iftu_isjammed=elapsedtime_s[i]
                    isiftujammed=True
                iftu_err=self.iftu.get_rmspositionerror((elapsedtime_s[i]-timeoflastiftu_s)+self.iftu_latency_s)
            
            pos_error_km[i]=np.sqrt(gps_err**2 + 
                                    evasive_err**2 + 
                                    ins_err**2 + 
                                    iftu_err**2 +
                                    self.offset_rms_positionerror_km**2)
        
        return elapsedtime_s,distanceflown_km,pos_error_km
        
