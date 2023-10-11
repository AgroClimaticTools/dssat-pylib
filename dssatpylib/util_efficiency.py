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

def r(observed, simulated):
    '''
    Calculates the Coefficient of Determination (R2) value between observed and 
    simulated data
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: R2 between observed and simulated data
    '''
    return stats.pearsonr(observed, simulated)

def dStat(observed, simulated):
    '''
    Performs Willmott (1981) Index of Agreement
    Willmott (1981) proposed an index of agreement (d) as a standardized measure
    of the degree of model prediction error which varies between 0 and 1. 
    The index of agreement represents the ratio of the mean square error and 
    the potential error. The agreement value of 1 indicates a perfect match, 
    and 0 indicates no agreement at all. The index of agreement can detect 
    additive and proportional differences in the observed and simulated means 
    and variances; however, d is overly sensitive to extreme values due to the 
    squared differences.
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: d-Stat between observed and simulated data
    '''
    num = np.sum((observed-simulated)**2)
    den = np.sum((abs(simulated-np.mean(observed)) + abs(observed-np.mean(observed)))**2)
    dStat = 1-num/den
    return dStat

def KGE(observed, simulated):
    '''
    Performs Kling-Gupta efficiency
    This goodness-of-fit measure was developed by Gupta et al. (2009) to provide
    a diagnostically interesting decomposition of the Nash-Sutcliffe efficiency
    (and hence MSE), which facilitates the analysis of the relative importance 
    of its different components (correlation, bias and variability) in the
    context of hydrological modelling Kling et al. (2012), proposed a revised
    version of this index, to ensure that the bias and variability ratios are 
    not cross-correlated.
    
    :param  observed: numpy array or list of observed data
    :param simulated: numpy array or list of simulated data
    
    :return float: KGE between observed and simulated data
    '''

    correlation_coefficient, p_value = stats.pearsonr(observed, simulated)

    KGE = 1 - ((correlation_coefficient - 1)**2 + \
        ((np.std(observed)/np.std(simulated))-1)**2 + \
        ((np.mean(observed)/np.mean(simulated))-1)**2)**0.5
    return KGE