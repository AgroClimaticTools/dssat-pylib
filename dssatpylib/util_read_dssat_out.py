# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: Utility functions to extract the DSSAT outputs from DSSAT generated
             '*.OUT' files and *.PTT file (only tested for potato crop)

"""
'=============================================================================='

import re
from datetime import date, datetime
from pathlib import Path
from typing import Union

import pandas as pd
from numpy import float32 as npFloat32
from numpy import nan as npNaN

# import polars as pl


'____________________________ function to check float__________________________'

def isfloat(value: Union[float, str, int]) -> bool:
    '''
    Check if the value is float
    
    :param value: str/float/int to check for float

    :return bool: if float returns True else False
    '''
    try:
        float(value)
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

'_____________ function to get data chunk indices from text file ______________'

def get_dataChunk_indices(text: str, Tfile=False) -> zip:
    '''
    Read the text from the dssat *.OUT files to return zip containing the 
    begining and ending indices of data in the file

    :param       text: text from the dssat *.OUT file in str
    :return       zip: zip containing the begining and ending indices of data 
                       in the file
    
    '''

    dataBegin_idx = [m.start()  for m in re.finditer(r"\n"+re.escape('@'), text)]
    if Tfile:
        newLine_idx = [db-1 for db in dataBegin_idx]
    else:
        newLine_idx = [m.start()  for m in re.finditer(r"\n\n", text)]
    lastLine_idx = [m.start()  for m in re.finditer(r"\n", text)][-1]
    dataEnd_idx = []
    for db in dataBegin_idx:
        for nl in newLine_idx:
            if nl>db:
                dataEnd_idx.append(nl)
                break
    dataEnd_idx.append(lastLine_idx)
    return zip(dataBegin_idx, dataEnd_idx)

'_____________ function to get data chunk indices from text file ______________'

def get_treatNums(text: str) -> list[int]:
    '''
    Get the number of treatments available in the DSSAT *.OUT file

    :param       text: text from the dssat *.OUT file in str
    :return treatNums: Total number of treatments

    '''
    treat_idx = [m.start()  for m in re.finditer('TREATMENT', text)]
    treatNums = [int(text[idx+9:idx+15].strip()) for idx in treat_idx]
    return treatNums

'________________________ function to read DSSAT Outputs ______________________'

def Read_DSSAT_Output(filePath: str|Path):
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
    filePath = Path(filePath)
    with open(filePath, 'r', errors='replace') as file:
        lines = file.read()
    
    data = ([line.strip().split() for line in lines[beg:end].split('\n') if line != '']
            for beg, end in get_dataChunk_indices(lines))
    
    df_gen = (pd.DataFrame.from_records(data[1:], columns=data[0]).astype(npFloat32) 
              for i, data in enumerate(data))
    
    
    treatNums = get_treatNums(lines)

    if 'Plant' in filePath.name:
        crops = (line.strip().split(' - ')[-1] 
                 for line in lines.split('\n') if line.startswith(' MODEL'))
        return df_gen, treatNums, crops

    return df_gen, treatNums


'__________________________ function for Summary.OUT __________________________'

def extract_required_dssat_outputs(filePath: str|Path, paramList: list[str],
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
                            listed above in str/Path
    :param       paramList: list of output parameters needed
    :param  cum_param_list: list of output parameters with cumulative values
    :param           daily: bool, True to convert values of cumulative 
                            parameters values to daily values else False
    :param   crop_sequence: bool, True to extract crop names, only available 
                             for PlantN and PlantGro outputs files

    :return df_required_dssat_outputs: Pandas dataframes of required DSSAT 
                                        outputs
    
    '''
    filePath = Path(filePath)

    'Reading file using Read_DSSAT_OUTPUT func'
    if 'Plant' in filePath.name:
        all_dssat_outputs, treatNums, crops = Read_DSSAT_Output(filePath)       # type: ignore
    else:
        all_dssat_outputs, treatNums = Read_DSSAT_Output(filePath)              # type: ignore
    
    df_list = []
    'r = Runs, treatNums = list of Number of Treatments in the file'
    for r, dssat_outputs in enumerate(all_dssat_outputs):
        dates = [datetime.strptime(str(int(year))+str(int(doy)), '%Y%j').date() 
                 for year, doy in zip(dssat_outputs['@YEAR'], dssat_outputs['DOY'])]
        
        rData = {}
        for prm in paramList:
            if prm in dssat_outputs.columns:                                    #type: ignore
                if daily == True and \
                        prm in cum_param_list:
                    'cum2daily converts cumulative values to daily'
                    rData[prm] = cum2daily([float(Val)
                                        for Val in dssat_outputs[prm]])         #type: ignore
                else:
                    rData[prm] = [float(Val)
                                  for Val in dssat_outputs[prm]]                #type: ignore
            else:
                rData[prm] = [npNaN for _ in dates]
        df = pd.DataFrame(rData)
        if treatNums is not None:
            df.loc[:,'@TRNO'] = [treatNums[r] for _ in range(len(df))]
        else:
            df.loc[:,'@TRNO'] = [r+1 for _ in range(len(df))]
        df.loc[:,'DATE'] = dates
        if crop_sequence:
            df.loc[:,'CROP'] = [crops[r] for _ in range(len(df))]                     #type: ignore
            df.set_index(['@TRNO', 'CROP', 'DATE'], inplace=True)
        else:
            df.set_index(['@TRNO', 'DATE'], inplace=True)
        df_list.append(df)

    df_required_dssat_outputs = pd.concat(df_list, axis=0)
    
    return df_required_dssat_outputs


'__________________________ function for Summary.OUT __________________________'

def Summary(fileDir: str|Path, paramList: list[str]):

    '''
    Extract required output parameters from Summary.OUT into a pandas dataframe 

    Call: extract_required_dssat_outputs

    :param    fileDir: complete file directory of Summary.OUT file 
    :param  paramList: list of output parameters needed in Summary.OUT

    :return df_required_dssat_outputs: Pandas dataframes of required DSSAT 
                                        outputs
    
    '''
    fileDir = Path(fileDir)
    with open(fileDir / 'Summary.OUT', 'r', errors='replace') as file:
        lines = file.read()
    
    data = ([line.strip().split() for line in lines[beg:end].split('\n') 
             if line != '']
            for beg, end in get_dataChunk_indices(lines))
    
    Summary_Data = (pd.DataFrame.from_records(data[1:], columns=data[0][1:]) 
                    for i, data in enumerate(data))

    df_required_dssat_outputs = next(Summary_Data)
    df_required_dssat_outputs.rename(columns={'TRNO': '@TRNO'}, inplace=True)   # type: ignore
    df_required_dssat_outputs.set_index(['@TRNO'], inplace=True)                # type: ignore
    df_required_dssat_outputs = df_required_dssat_outputs.loc[:, paramList]     # type: ignore

    return df_required_dssat_outputs


'_________________________ function for PlantGro.OUT __________________________'

def PlantGro(fileDir: str|Path, paramList: list[str], 
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
    fileDir = Path(fileDir)
    filePath = fileDir / 'PlantGro.OUT'
    cum_param_list = ['SNW0C', 'SNW1C']
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence)
    return df_outputs


'__________________________ function for PlantN.OUT ___________________________'

def PlantN(fileDir: str|Path, paramList: list[str],
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
    fileDir = Path(fileDir)
    filePath = fileDir / 'PlantN.OUT'
    cum_param_list = ['NUPC', 'SNN0C', 'SNN1C']
    df_outputs = extract_required_dssat_outputs(filePath, paramList,
                                                cum_param_list, daily,
                                                crop_sequence)
    return df_outputs


'__________________________ function for SoilNi.OUT ___________________________'

def SoilNi(fileDir: str|Path, paramList: list[str], daily=True):
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

    fileDir = Path(fileDir)
    filePath = fileDir / 'SoilNi.OUT'
    cum_param_list = ['NAPC', 'NMNC', 'NITC', 'NDNC', 'NIMC',
                      'AMLC', 'NNMNC', 'NUCM', 'NLCC', 'TDFC']
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence=False)
    return df_outputs


'__________________________ function for SoilWat.OUT __________________________'

def SoilWat(fileDir: str|Path, paramList: list[str], daily: bool = True):
    '''
    Extract required output parameters from SoilWat.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param     fileDir: complete file directory of SoilWat.OUT file
    :param   paramList: list of output parameters needed
    :param       daily: bool, True to convert values of cumulative 
                         parameters values to daily values else False

    :return df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    fileDir = Path(fileDir)
    filePath = fileDir / 'SoilWat.OUT'
    cum_param_list = ['ROFC', 'DRNC', 'PREC', 'IR#C', 'IRRC', 'TDFC']
    df_outputs = extract_required_dssat_outputs(str(filePath), paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence=False)
    return df_outputs


'____________________________ function for ET.OUT _____________________________'

def ET(fileDir: str|Path, paramList: list[str],
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

    fileDir = Path(fileDir)
    filePath = fileDir / 'ET.OUT'
    cum_param_list = ['ETAC','EPAC','ESAC','EFAC','EMAC']
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list, daily, 
                                                crop_sequence=False)
    return df_outputs


'__________________________ function for Weather.OUT __________________________'

def Weather(fileDir: str|Path, paramList: list[str]):
    '''
    Extract required output parameters from Weather.OUT into a pandas dataframe

    Call: extract_required_dssat_outputs

    :param     fileDir: complete file directory of Weather.OUT file
    :param   paramList: list of output parameters needed

    :return df_outputs: Pandas dataframes of required DSSAT outputs
    
    '''

    fileDir = Path(fileDir)
    filePath = fileDir / 'Weather.OUT'
    df_outputs = extract_required_dssat_outputs(filePath, paramList, 
                                                cum_param_list=[''], daily=False, 
                                                crop_sequence = False)
    return df_outputs


'_______ function to calculate Soil C:N from SOMLITC.OUT & SOMLITN.OUT ________'

def CN_Ratio(fileDir: str|Path):
    '''
    Extracting following variables from SOMLITC_Data & SOMLITN_Data:
    SCS20D    Organic C (SOM) in top 20 cm (kg/ha)
    SNS20D    Organic N (SOM) in top 20 cm (kg/ha)

    '''
    fileDir = Path(fileDir)
    SOMLITC_Data = Read_DSSAT_Output(fileDir / 'SOMLITC.OUT')
    SOMLITN_Data = Read_DSSAT_Output(fileDir / 'SOMLITN.OUT')

    nRuns = len(SOMLITC_Data)
    Year = [str(Val) for i in range(nRuns) for Val in SOMLITC_Data[i]['YEAR']]  # type: ignore
    DOY = [str(Val) for i in range(nRuns) for Val in SOMLITC_Data[i]['DOY']]    # type: ignore
    YearDOY = zip(Year, DOY)
    DATE = [datetime.strptime(Year+DOY, '%Y%j').date() for Year, DOY in YearDOY]

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

def SoilWatBal(fileDir: str|Path, RunStart: int=1, RunEnd = 'last'):
    """
    Extract the soil water balance from SoilWatBal.OUT file

    :param     fileDir: complete file directory of SoilWatBal.OUT file
    :param    RunStart: Starting Run, defaults to 1
    :param      RunEnd: Ending Run, defaults to 'last'
    :return         df: Pandas dataframes of required DSSAT outputs

    """    
    fileDir = Path(fileDir)
    filePath = fileDir / 'SoilWatBal.OUT'        
    WatBalData = {'Run'               : [], 'Treatment Name'    : [],
                  'Planting Dates'    : [], 'Harvesting Dates'  : [],
                  'Soil Water (Start)': [], 'Soil Water (Final)': [],
                  'Precipitation'     : [], 'Drainage'          : [],
                  'Tiledrain flow'    : [], 'Runoff'            : [],
                  'Evapotranspiration': []}
    with open(filePath, 'r', errors='replace') as Fswb:
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

def read_dssat_obsdata(filePath: str|Path, paramList: list = ['ALL'], sort_index = True):
    '''
    Read DSSAT experiment observation file
    Initially build to read Potato- *.PTT file but could be used for other crops

    :param    filePath: complete file path to *.*TT file or *.csv file in same
                        format
    :param   paramList: list of output parameters needed or 'ALL' for all the 
                        parameters

    :return df: Pandas dataframes of required DSSAT outputs
    
    '''
    filePath = Path(filePath)
    if filePath.suffix == '.csv':
        try: 
            df = pd.read_csv(filePath, parse_dates=['DATE'])
            df['DATE'] = [val.to_pydatetime().date()
                          for val in df['DATE']]
        except: df = pd.read_csv(filePath)
    else:
        with open(filePath, 'r', errors='replace') as file:
            lines = ''
            for line in file.readlines():
                if not line.startswith('!'):
                    lines = lines + line.split('!')[0]

        data = ([line.strip().split() for line in lines[beg:end].split('\n') 
                 if line.strip() != '']
                for beg, end in get_dataChunk_indices(lines, Tfile=True))

        df_list = [pd.DataFrame.from_records(data[1:], columns=data[0]).astype(str) 
                    for i, data in enumerate(data)]
        df = pd.concat(df_list, axis=0)
        df['@TRNO'] = df['@TRNO'].astype(int)
        
    if not isinstance(df['DATE'][0], date):
        df['DATE'] = [datetime.strptime(val, '%y%j').date()
                      for val in df.loc[:, 'DATE'].values]
    
    cols = df.columns.difference(['DATE','@TRNO'])
    df[cols] = df[cols].astype(float).astype(npFloat32)
    
    df.replace(-99.0, npNaN, inplace=True)
    
    try: df.rename(columns={'@TRNO':'TRNO'}, inplace=True)
    except: pass
    
    df.set_index(['TRNO', 'DATE'], inplace=True)

    'If all parameters are required, fetch all'
    'Else fetch listed parameters while calling this func'
    if paramList[0] == 'ALL':
        if sort_index:
            return df.sort_index()
        else:
            return df
    else:
        if sort_index:
            return df.loc[:,paramList].sort_index()
        else:
            return df.loc[:,paramList]

'___________________________ functions to read X file _________________________'

def delimitate_header_indices(section_header_str):
    start_indices = [0]+[i for i, character in enumerate(section_header_str)
                           if character == ' ' and section_header_str[i+1] != ' ']
    end_indices = start_indices[1:] + [len(section_header_str)+20]
    return list(zip(start_indices, end_indices))

def sep_sections_in_dict(exp_file):
    with open(exp_file, 'r', errors='replace') as opened_exp_file:
        sec_str_dict = {}
        startfilling = False
        each_sec = ''
        sec_title = ''
        for line in opened_exp_file.readlines():
            if line.startswith('!'):
                continue
            if line.startswith('*'):
                startfilling = True
                sec_title = line.strip().split(':')[0][1:].split('  ')[0]
            # if sec_title == 'SIMULATION':
            #     each_sec = each_sec + line
            else:
                if startfilling:
                    each_sec = each_sec + line
                if line.startswith('\n'):
                    sec_str_dict[sec_title] = each_sec
                    startfilling = False
                    each_sec = ''
        # if sec_title == 'SIMULATION':
        #     sec_str_dict[sec_title] = each_sec
    return sec_str_dict

def get_section_txt(exp_file, section_name):
    with open(exp_file, 'r', errors='replace') as opened_exp_file:
        fileText = opened_exp_file.read()
    regex = "(?s)(?<="+section_name+")(.*?)(?=\n\n)"
    sec_text = re.search(regex, fileText)
    if sec_text != None:
        return (sec_text.group(0))
    else:
        return None

def get_section_df(exp_file: Path, section_name: str):
    # section_str_dict = sep_sections_in_dict(exp_file)
    # section_str = section_str_dict[section_name]
    section_str = get_section_txt(exp_file, section_name)
    if section_str is not None:
        all_section_rows = section_str.split('\n')[1:]
        tables_in_section_rows = []
        for section_row in all_section_rows:
            if section_row.startswith('!'):
                continue
            if section_row.startswith('@') and ~section_row.startswith('@ '):
                tables_in_section_rows.append([])
                tables_in_section_rows[-1].append(section_row)
            else:
                tables_in_section_rows[-1].append(section_row)
        df_list = []
        header_indices_list = []
        for table_row in tables_in_section_rows:        
            section_header_str = table_row[0]
            section_data_str_list = table_row[1:]
            data_rows = []
            header_indices = delimitate_header_indices(section_header_str)
            for section_data_str in section_data_str_list:
                data_rows.append([section_data_str[i:j].strip()
                                for i, j in header_indices])
            sec_header = section_header_str.split()
            df = pd.DataFrame(data=data_rows, columns=sec_header)
            df_list.append(df)
            header_indices_list.append(header_indices)
        return df_list, header_indices_list
    else:
        return None

'=============================================================================='