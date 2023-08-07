# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: Calculates model efficiencies and other model validation metrics

"""
import math
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats

# Computes RMSE coefficient
def RMSE(observed, simulated):
    '''
    Calculates the Root Mean Squared Error (RMSE) value of the simulated data

    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: RMSE
    '''
    return mean_squared_error(observed, simulated, squared=False)

# Computes RMSE coefficient
def nRMSE(observed, simulated):
    '''
    Calculates the Relative Root Mean Squared Error (RMSE) value of the simulated data

    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: RRMSE
    '''
    return mean_squared_error(observed, simulated, squared=False)/np.mean(observed)

# Computes RSR coefficient
def RSR(observed, simulated):
    '''
    Calculates the Root Mean Squared Error to Standard deviation Ratio (RSR)
    value of the simulated data

    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: RSR
    '''
    return mean_squared_error(observed, simulated, squared=False)/np.std(observed)

# Computes Nash Sutcliffe Efficiency
def NSE(observed, simulated):
    '''
    Calculates the Nash Sutcliffe Efficienct (NSE) value of the simulated data
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: NSE
    '''
    num = np.sum((observed-simulated)**2)
    den = np.sum((observed-np.mean(simulated))**2)
    NSE = 1-num/den
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

def dStat(observed, simulated):
    '''
    Performs the (one-sample or two-sample) Kolmogorov-Smirnov (d-stat) test for
    goodness of fit between observed and simulated data
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: d-Stat between observed and simulated data
    '''
    return stats.kstest(observed, simulated).pvalue
