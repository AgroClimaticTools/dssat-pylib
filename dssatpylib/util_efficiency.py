# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: Calculates model efficiencies and other model validation metrics

"""
import math
from sklearn.metrics import r2_score

# Computes RMSE coefficient
def RMSE(observed, simulated):
    '''
    Calculates the Root Mean Squared Error (RMSE) value of the simulated data

    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: RMSE in the simulated data
    '''
    sum = 0.
    for i in range(len(observed)):
            sum += ((observed[i]-simulated[i])**2)
    sum = sum / len(observed)
    return (math.sqrt(sum))

# Computes Nash Sutcliffe Efficiency
def NSE(observed, simulated):
    '''
    Calculates the Nash Sutcliffe Efficienct (NSE) value of the simulated data
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: NSE in the simulated data
    '''
    sum_obs, diff_num, diff_den = 0.0, 0.0, 0.0
    for record in observed:
        sum_obs += record
    mean_obs = sum_obs/len(observed)
    for count in range(len(observed)):
        diff_num += pow((observed[count]-simulated[count]), 2)
        diff_den += pow((observed[count]-mean_obs), 2)
    NSE = 1-(diff_num/diff_den)
    return (NSE)

def R2(observed, simulated):
    '''
    Calculates the Coefficient of Determination (R2) value between observed and 
    simulated data
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: R2 between observed and simulated data
    '''
    return r2_score(observed, simulated)
    
