# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: Utility functions to extract the DSSAT outputs from DSSAT generated
             '*.OUT' files and *.PTT file (only tested for potato crop)

"""
'=============================================================================='

import os
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

'____________________________ function to check float__________________________'

def isfloat(var):
    '''
    Check if the variable provided is float or not

    :param   var: any data type variable
    :return bool: 'True' if var is float else 'False'

    '''
    try:
        float(var)
        return True
    except ValueError:
        return False


'__________________ function to convert cumulative to daily ___________________'

def cum2daily(cumdata: list[float]) -> list[float]:
    '''
    Converts cumulative values to daily values. The function can handle several 
    series of stacked cumulative values in 1-Dimensional list of floats

    :param    cumdata: list of cumulative values in float
    :return dailydata: list of daily values in float
    
    '''
    dailydata = [cumdata[0]]
    for i in range(1, len(cumdata)):
        if cumdata[i] < cumdata[i-1]:
            dailydata.append(cumdata[i])
        else:
            dailydata.append(cumdata[i]-cumdata[i-1])
    return dailydata


'________________________ function to read DSSAT Outputs ______________________'

def Read_DSSAT_Output(filePath: str):
    '''
    Read several DSSAT generated output files (*.OUT) into a list of pandas 
    dataframes. Currently, the functions is tested for PlantGro, PlantN, 
    Summary, SoilWat, SoilWatBal, SoilNi, ET, Weather, observed DSSAT generated
    file of Potato with *.PTT extension

    Call by: extract_required_dssat_outputs, Summary

    :param        filePath: complete file path of the interested *.OUT file 
                            listed above in str

    :return df_list, crops: df_list of the pandas dataframes for individual 
                             DSSAT run, crops is returned when PlantN/PlantGro
                             output file of DSSAT is read.    
    
    '''
    with open(filePath, 'r') as f:
        n = 0
        data = []
        crops = []
        runs = []
        for line in f:
            if line.startswith('*RUN'):
                runs.append(line.strip().split()[1])
            elif line.startswith(' MODEL'):
                crops.append(line.strip().split(' - ')[-1])
            elif line.startswith('@'):
                n = 1
                header = line[1:].replace('.', '').strip().split()
                data.append([header])
            elif line.startswith('\n'):
                n = 0
            if n == 1 and not line.startswith('@'):
                data[-1].append(line.strip().split())
    
    # PlantGro.OUT/PlantN.OUT
    if 'Plant' in filePath:
        df_list = [pd.DataFrame.from_records(data[i][1:], columns=data[i][0])
                   for i in range(len(data))]
        print(df_list, filePath)
        return df_list, crops

    else:
        df_list = [pd.DataFrame.from_records(data[i][1:], columns=data[i][0])
                   for i in range(len(data))]
        return df_list


'__________________________ function for Summary.OUT __________________________'

def extract_required_dssat_outputs(filePath: str, paramList: list[str],
                                   cum_param_list: list[str],
                                   daily: bool = True, 
                                   crop_sequence: bool = False):
    '''
    Extract required output parameters from the DSSAT output files (*.OUT) into 
    a pandas dataframe. 
    Currently, the functions is tested for PlantGro, PlantN, 
    Summary, SoilWat, SoilWatBal, SoilNi, ET, Weather, observed DSSAT generated
    file of Potato with *.PTT extension

    Call:    Read_DSSAT_Output
    Call by: PlantGro, PlantN, SoilWat, SoilNi, ET

    :param        filePath: complete file path of the interested *.OUT file 
                             listed above in str
    :param       paramList: list of output parameters needed
    :param  cum_param_list: list of output parameters with cumulative values
    :param           daily: bool, True to convert values of cumulative 
                            parameters values to daily values else False
    :param   crop_sequence: bool, True to extract crop names, only available 
                             for PlantN and PlantGro outputs files

    :return df_required_dssat_outputs: Pandas dataframes of required DSSAT 
                                        outputs
    
    '''

    'Reading file using Read_DSSAT_OUTPUT func'
    if 'Plant' in filePath:
        all_dssat_outputs, crops = Read_DSSAT_Output(filePath)
    else:
        all_dssat_outputs = Read_DSSAT_Output(filePath)

    'nRuns = number of Runs/Treatments'
    nRuns = len(all_dssat_outputs)
    df_list = []
    
    for r in range(nRuns):
        year = [int(Val) for Val in all_dssat_outputs[r]['YEAR']]               #type: ignore
        doy = [int(Val) for Val in all_dssat_outputs[r]['DOY']]                 #type: ignore
        year_doy = zip(year, doy)
        dates = [date(year, 1, 1) + timedelta(doy-1) for year, doy in year_doy]
        rData = {}
        for prm in paramList:
            if prm in all_dssat_outputs[r].columns.values:                      #type: ignore
                if daily == True and \
                        prm in cum_param_list:
                    'cum2daily converts cumulative values to daily'
                    rData[prm] = cum2daily([float(Val)
                                        for Val in all_dssat_outputs[r][prm]])  #type: ignore
                else:
                    rData[prm] = [float(Val)
                                  for Val in all_dssat_outputs[r][prm]]         #type: ignore
            else:
                rData[prm] = [np.nan for _ in dates]
        df = pd.DataFrame(rData)
        df['@TRNO'] = [r+1 for _ in range(len(df))]
        df['DATE'] = dates
        if crop_sequence:
            df['CROP'] = [crops[r] for _ in range(len(df))]                     #type: ignore
            df.set_index(['@TRNO', 'CROP', 'DATE'], inplace=True)
        else:
            df.set_index(['@TRNO', 'DATE'], inplace=True)
        df_list.append(df)

    df_required_dssat_outputs = pd.concat(df_list, axis=0)
    
    return df_required_dssat_outputs


'__________________________ function for Summary.OUT __________________________'

def Summary(fileDir: str, paramList: list[str]):

    '''
    Extract required output parameters from Summary.OUT into a pandas dataframe 

    Call: extract_required_dssat_outputs

    :param    fileDir: complete file directory of Summary.OUT file 
    :param  paramList: list of output parameters needed in Summary.OUT

    :return df_required_dssat_outputs: Pandas dataframes of required DSSAT 
                                        outputs
    
    '''
    
    Summary_Data = Read_DSSAT_Output(fileDir + '//Summary.OUT')
    df_required_dssat_outputs = Summary_Data[0]
    df_required_dssat_outputs.rename(columns={'TRNO': '@TRNO'}, inplace=True)   # type: ignore
    df_required_dssat_outputs.set_index(['@TRNO'], inplace=True)                # type: ignore
    df_required_dssat_outputs = df_required_dssat_outputs.loc[:, paramList]     # type: ignore

    return df_required_dssat_outputs


'_________________________ function for PlantGro.OUT __________________________'

def PlantGro(fileDir: str, paramList: list[str], 
             daily: bool = True, crop_sequence: bool = False):
    '''
    Extract required output parameters from PlantGro.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param       fileDir: complete file directory of PlantGro.OUT file
    :param     paramList: list of output parameters needed
    :param         daily: bool, True to convert values of cumulative 
                          parameters values to daily values else False
    :param crop_sequence: bool, True to extract crop names

    :return   df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    filePath = fileDir + '//PlantGro.OUT'
    cum_param_list = ['SNW0C', 'SNW1C']
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence)
    return df_outputs


'__________________________ function for PlantN.OUT ___________________________'

def PlantN(fileDir: str, paramList: list[str],
           daily: bool = True, crop_sequence: bool = False):
    '''
    Extract required output parameters from PlantN.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param       fileDir: complete file directory of PlantN.OUT file
    :param     paramList: list of output parameters needed
    :param         daily: bool, True to convert values of cumulative 
                          parameters values to daily values else False
    :param crop_sequence: bool, True to extract crop names

    :return   df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    filePath = fileDir + '//PlantN.OUT'
    cum_param_list = ['NUPC', 'SNN0C', 'SNN1C']
    df_outputs = extract_required_dssat_outputs(filePath, paramList,
                                                cum_param_list, daily,
                                                crop_sequence)
    return df_outputs


'__________________________ function for SoilNi.OUT ___________________________'

def SoilNi(fileDir: str, paramList: list[str], daily=True):
    '''
    Extract required output parameters from SoilNi.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param     fileDir: complete file directory of SoilNi.OUT file
    :param   paramList: list of output parameters needed
    :param       daily: bool, True to convert values of cumulative 
                         parameters values to daily values else False

    :return df_outputs: Pandas dataframes of required DSSAT 
                             outputs
    
    '''

    filePath = fileDir + '//SoilNi.OUT'
    cum_param_list = ['NAPC', 'NMNC', 'NITC', 'NDNC', 'NIMC',
                      'AMLC', 'NNMNC', 'NUCM', 'NLCC', 'TDFC']
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence=False)
    return df_outputs


'__________________________ function for SoilWat.OUT __________________________'

def SoilWat(fileDir: str, paramList: list[str], daily: bool = True):
    '''
    Extract required output parameters from SoilWat.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param     fileDir: complete file directory of SoilWat.OUT file
    :param   paramList: list of output parameters needed
    :param       daily: bool, True to convert values of cumulative 
                         parameters values to daily values else False

    :return df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    filePath = Path(fileDir) / 'SoilWat.OUT'
    cum_param_list = ['ROFC', 'DRNC', 'PREC', 'IR#C', 'IRRC', 'TDFC']
    df_outputs = extract_required_dssat_outputs(str(filePath), paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence=False)
    return df_outputs


'____________________________ function for ET.OUT _____________________________'

def ET(fileDir: str, paramList: list[str],
       daily: bool = True):
    '''
    Extract required output parameters from ET.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param     fileDir: complete file directory of ET.OUT file
    :param   paramList: list of output parameters needed
    :param       daily: bool, True to convert values of cumulative 
                             parameters values to daily values else False

    :return df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    filePath = fileDir + '//ET.OUT'
    cum_param_list = ['ETAC','EPAC','ESAC','EFAC','EMAC']
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence=False)
    return df_outputs


'__________________________ function for Weather.OUT __________________________'

def Weather(fileDir: str, paramList: list[str]):
    '''
    Extract required output parameters from Weather.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param     fileDir: complete file directory of Weather.OUT file
    :param   paramList: list of output parameters needed

    :return df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    filePath = fileDir + '//Weather.OUT'
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list=[''], daily=False, 
                                                crop_sequence = False)
    return df_outputs


'_______ function to calculate Soil C:N from SOMLITC.OUT & SOMLITN.OUT ________'

def CN_Ratio(fileDir: str):
    SOMLITC_Data = Read_DSSAT_Output(fileDir + '//SOMLITC.OUT')
    SOMLITN_Data = Read_DSSAT_Output(fileDir + '//SOMLITN.OUT')
    '''
    Extracting following variables from SOMLITC_Data & SOMLITN_Data:
    SCS20D    Organic C (SOM) in top 20 cm (kg/ha)
    SNS20D    Organic N (SOM) in top 20 cm (kg/ha)

    '''
    nRuns = len(SOMLITC_Data)
    Year = [int(Val) for i in range(nRuns) for Val in SOMLITC_Data[i]['YEAR']]  # type: ignore
    DOY = [int(Val) for i in range(nRuns) for Val in SOMLITC_Data[i]['DOY']]    # type: ignore
    YearDOY = zip(Year, DOY)
    DATE = [date(Year, 1, 1) + timedelta(DOY-1) for Year, DOY in YearDOY]

    SCS20D = [Val for i in range(nRuns) for Val in SOMLITC_Data[i]['SCS20D']]   # type: ignore
    SNS20D = [Val for i in range(nRuns) for Val in SOMLITN_Data[i]['SNS20D']]   # type: ignore

    CN_Ratio = []
    
    if len(SCS20D) == len(SNS20D):
        for i in range(len(SCS20D)):
            CN_Ratio.append(float(SCS20D[i])/float(SNS20D[i]))
    else:
        print ("Data length for SCS20D and SNS20D are not same")
        print (len(SCS20D),len(SNS20D))
        CN_Ratio = []

    return DATE, CN_Ratio


'_______________________ function for SoilWatBal.OUT __________________________'

def SoilWatBal(fileDir: str, RunStart: int=1, RunEnd = 'last'):
    File = fileDir + '//SoilWatBal.OUT'        
    WatBalData = {'Run'               : [], 'Treatment Name'    : [],
                  'Planting Dates'    : [], 'Harvesting Dates'  : [],
                  'Soil Water (Start)': [], 'Soil Water (Final)': [],
                  'Precipitation'     : [], 'Drainage'          : [],
                  'Tiledrain flow'    : [], 'Runoff'            : [],
                  'Evapotranspiration': []}
    with open(File) as Fswb:
        param = 0
        for line in Fswb:    
            if line.startswith('*RUN'):
                Run, Tname = line.split(':')
                WatBalData['Run'].append(Run.strip()[1:].split()[-1])
                WatBalData['Treatment Name'].append(' '.join(
                    Tname.split()[:-3]))
                evapotranspiration = 0
            
            if line.startswith('!     Soil H20 (start)'):
                param = 1
            
            if line.startswith('!     Final Balance'):
                key, val = line[6:-8].strip(), line[-8:].strip()
                if key in WatBalData.keys():
                        WatBalData[key].append(float(val)) 
                param = 0

            if param == 1:
                key, val = line[6:-8].strip(), line[-8:].strip()
                if 'start' in key:
                    plant_yyyy_doy = key.split()[-1]
                    plant_date = datetime.strptime(plant_yyyy_doy, '%Y/%j')
                    WatBalData['Planting Dates'].append(plant_date)
                    WatBalData['Soil Water (Start)'].append(float(val))
                elif 'final' in key:
                    harvest_yyyy_doy = key.split()[-1]
                    harvest_date = datetime.strptime(harvest_yyyy_doy, '%Y/%j')
                    WatBalData['Harvesting Dates'].append(harvest_date)
                    WatBalData['Soil Water (Final)'].append(float(val))                    
                else:
                    if key in WatBalData.keys():
                        WatBalData[key].append(-float(val))
                    elif 'Evaporation' in key:
                        evapotranspiration = evapotranspiration + float(val)    # type: ignore
                    elif 'Transpiration' in key:
                        evapotranspiration = evapotranspiration + float(val)    # type: ignore
                        WatBalData['Evapotranspiration'].append(
                            -evapotranspiration)
                        
    WatBal_df = pd.DataFrame(WatBalData)
    WatBal_df.set_index('Run', inplace=True)
    WatBal_df['Soil Water Lost'] = WatBal_df['Soil Water (Start)'] - \
                                   WatBal_df['Soil Water (Final)']
    WatBal_df['Precipitation'] = -WatBal_df['Precipitation']
    if RunEnd == 'last':
        return WatBal_df.iloc[RunStart-1:,:]
    else:
        return WatBal_df.iloc[RunStart-1:RunEnd,:]
    

'__________________________ function to read *.PTT ____________________________'

def read_dssat_obsdata(filePath: str, paramList: list = ['ALL']):
    '''
    Read DSSAT experiment observation file
    Initially build to read Potato- *.PTT file but could be used for other crops

    :param    filePath: complete file path to *.*TT file or *.csv file in same
                        format
    :param   paramList: list of output parameters needed or 'ALL' for all the 
                        parameters

    :return df: Pandas dataframes of required DSSAT outputs
    
    '''
    if filePath.endswith('.csv'):
        try: 
            df = pd.read_csv(filePath, parse_dates=['DATE'])
            df['DATE'] = [val.to_pydatetime().date()
                          for val in df['DATE']]
        except: df = pd.read_csv(filePath)
    else:
        df = pd.read_fwf(filePath, colspecs='infer', infer_nrows=100,
                         skiprows=5)
    if not isinstance(df['DATE'][0], date):
        df['DATE'] = [date(2000+int(str(val)[:2]), 1, 1) + \
                       timedelta(int(str(val)[-3:])-1)
                       for val in df.loc[:, 'DATE'].values]        

    df.replace(-99.0, np.nan, inplace=True)
    try: df.rename(columns={'@TRNO':'TRNO'}, inplace=True)
    except: pass
    df.set_index(['TRNO', 'DATE'], inplace=True)

    'If all parameters are required to fetch'
    'Else listed parameters while calling this func'
    if paramList[0] == 'ALL':
        return df.sort_index()
    else:
        return df.loc[:,paramList].sort_index()

'=============================================================================='