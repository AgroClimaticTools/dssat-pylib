# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: To read, update and create soil profile in any *.SOL file

"""

from typing import Union

import pandas as pd

'============================= utility functions =============================='

'_______________________________ Check if float _______________________________'

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


'_________________________ function to format inputs __________________________'

def formatInput(input_to_format, space_available: int, decimal: int = 0) -> str:

    '''
    Format the unformatted input with required padding and rounding

    :param input_to_format: str/float/int, unformatted input
    :param space_available: int, space available to fit unformatted input
    :param         decimal: int, numbers after decimal

    :return formatted_string: str, formatted string
    '''

    if not isfloat(input_to_format):
        formatted2str = str(input_to_format)
    elif isfloat(input_to_format) and int(input_to_format) == -99:
        formatted2str = str(int(input_to_format))
    else:
        if decimal != 0:
            formatting = '{:.'+str(decimal)+'f}'
            formatted2str = formatting.format(input_to_format)
        else:
            formatted2str = str(int(input_to_format))

    padSpace = (space_available-len(formatted2str))*' '
    formatted_input = padSpace + formatted2str
    return formatted_input


'============================ DSSAT Soil Functions ============================'

'________________________ function for read *.SOL file ________________________'

def read_soil_profile(soilFilePath: str, soil_id: str, OnlyText: bool = False) \
    -> Union[pd.DataFrame, pd.DataFrame, list[str], str, list[str]] | str:
    '''
    Read the soil data from *.SOL file of the DSSAT
    
    :param soilFilePath: complete path to the soil file (*.SOL)
    :param      soil_id: Soil ID followed with an asterick sign (*)
    :param     OnlyText: bool, if True, the function will return soil data in 
                         the text format otherwise it will return soil data in
                         the text as well as pandas dataframe format

    :return         soil_info_df: pandas dataframe of the second table in the 
                                  soil profile which contains general soil 
                                  information
    :return soil_layered_info_df: pandas dataframe of the third table in the 
                                  soil profile which contains layered soil 
                                  profile information
    :return           soil_lines: list of all the lines in the soil data
    :return            soil_text: soil data in text format
    :return      headertext_list: list of the text up to header of the second
                                  table and text of third table header
    '''
    section = []
    soil_text = ''
    soil_lines = []
    headers = []
    with open(soilFilePath) as Fsoil:
        param = 0
        for line in Fsoil:
            if line.startswith('*'+soil_id):
                param = 1
                soil_text = soil_text + line
                soil_lines.append(line)
                continue
            if param == 1:
                if line.startswith('*'):
                    param = 0
                    break
                elif line == '\n' or line.startswith('!') or line.strip() == '':
                    soil_text = soil_text + line
                    continue
                elif line.startswith('@'):
                    section.append([])
                    headers.append(line)
                section[-1].append(line.split('!')[0].strip())
                soil_text = soil_text + line
                soil_lines.append(line)
    
    if OnlyText:
        return soil_text
    table_header = section[1][0][2:].split()
    table_data = [[float(val) if isfloat(val) else val for val in line.split()] 
                    for line in section[1][1:]]
    soil_info_df = pd.DataFrame(table_data, columns=table_header)

    soil_layered_info_df_list = []
    for Data in section[2:]:
        table_header = Data[0][2:].split()
        table_data = [[float(val) if isfloat(val) else val for val in line.split()]
                    for line in Data[1:]]
        df = pd.DataFrame(table_data, columns=table_header)
        df.set_index('SLB', inplace=True)
        soil_layered_info_df_list.append(df)
    soil_layered_info_df = pd.concat(soil_layered_info_df_list, axis=1).reset_index()
    headertext_list = [''.join(soil_lines[:4])]+headers[2:]
    
    return soil_info_df, soil_layered_info_df, soil_lines, \
        soil_text, headertext_list                                              # type: ignore


'______________________ function for generate *.SOL file ______________________'

def create_soil_profile(soil_layered_info_df, soil_info_df, headertext_list):
    '''
    Create the soil profile in the string format
    :param soil_layered_info_df: pandas dataframe, the third table in the 
                                 soil profile which contains layered soil 
                                 profile information
    :param         soil_info_df: pandas dataframe, the second table in the 
                                 soil profile which contains general soil 
                                 information
    :param      headertext_list: list of the text up to header of the second
                                  table and text of third table header
    
    :return text: str, soil profile for given data
    '''
    text = headertext_list[0]

    SCOM = formatInput(soil_info_df.loc[0,'SCOM'], 6, decimal=0)
    SALB = formatInput(soil_info_df.loc[0,'SALB'], 6, decimal=2)
    SLU1 = formatInput(soil_info_df.loc[0,'SLU1'], 6, decimal=1)
    SLDR = formatInput(soil_info_df.loc[0,'SLDR'], 6, decimal=2)
    SLRO = formatInput(soil_info_df.loc[0,'SLRO'], 6, decimal=1)
    SLNF = formatInput(soil_info_df.loc[0,'SLNF'], 6, decimal=2)
    SLPF = formatInput(soil_info_df.loc[0,'SLPF'], 6, decimal=2)
    SMHB = formatInput(soil_info_df.loc[0,'SMHB'], 6)
    SMPX = formatInput(soil_info_df.loc[0,'SMPX'], 6)
    SMKE = formatInput(soil_info_df.loc[0,'SMKE'], 6)
    text = text + ''.join([SCOM, SALB, SLU1, SLDR, SLRO, SLNF, SLPF, SMHB, SMPX,
                           SMKE])+'\n'
    text = text + headertext_list[1]
    for row in range(soil_layered_info_df.shape[0]):
        SLB  = formatInput(soil_layered_info_df.loc[row, 'SLB'], 6)
        SLMH = formatInput(soil_layered_info_df.loc[row,'SLMH'], 5)
        SLLL = formatInput(soil_layered_info_df.loc[row,'SLLL'], 7, decimal=3)
        SDUL = formatInput(soil_layered_info_df.loc[row,'SDUL'], 6, decimal=3)
        SSAT = formatInput(soil_layered_info_df.loc[row,'SSAT'], 6, decimal=3)
        SRGF = formatInput(soil_layered_info_df.loc[row,'SRGF'], 6, decimal=3)
        SSKS = formatInput(soil_layered_info_df.loc[row,'SSKS'], 6, decimal=2)
        SBDM = formatInput(soil_layered_info_df.loc[row,'SBDM'], 6, decimal=2)
        SLOC = formatInput(soil_layered_info_df.loc[row,'SLOC'], 6, decimal=2)
        SLCL = formatInput(soil_layered_info_df.loc[row,'SLCL'], 6, decimal=1)
        SLSI = formatInput(soil_layered_info_df.loc[row,'SLSI'], 6, decimal=1)
        SLCF = formatInput(soil_layered_info_df.loc[row,'SLCF'], 6, decimal=1)
        SLNI = formatInput(soil_layered_info_df.loc[row,'SLNI'], 6, decimal=3)
        SLHW = formatInput(soil_layered_info_df.loc[row,'SLHW'], 6, decimal=1)
        SLHB = formatInput(soil_layered_info_df.loc[row,'SLHB'], 6, decimal=1)
        SCEC = formatInput(soil_layered_info_df.loc[row,'SCEC'], 6, decimal=1)
        SADC = formatInput(soil_layered_info_df.loc[row,'SADC'], 6, decimal=2)
        text = text + ''.join([SLB,  SLMH, SLLL, SDUL, SSAT, SRGF, SSKS, SBDM, 
                               SLOC, SLCL, SLSI, SLCF, SLNI, SLHW, SLHB, SCEC,
                               SADC])+'\n'
    if 'SLPX' in soil_layered_info_df.columns and 'ALFVG' in soil_layered_info_df.columns:
        text = text + headertext_list[2]
        for row in range(soil_layered_info_df.shape[0]):
            SLB   = formatInput(soil_layered_info_df.loc[row,  'SLB'], 6)
            SLPX  = formatInput(soil_layered_info_df.loc[row, 'SLPX'], 6, decimal=1)
            SLPT  = formatInput(soil_layered_info_df.loc[row, 'SLPT'], 6)
            SLPO  = formatInput(soil_layered_info_df.loc[row, 'SLPO'], 6, decimal=3)
            CACO3 = formatInput(soil_layered_info_df.loc[row,'CACO3'], 6, decimal=3)
            SLAL  = formatInput(soil_layered_info_df.loc[row, 'SLAL'], 6, decimal=3)
            SLFE  = formatInput(soil_layered_info_df.loc[row, 'SLFE'], 6, decimal=3)
            SLMN  = formatInput(soil_layered_info_df.loc[row, 'SLMN'], 6, decimal=3)
            SLBS  = formatInput(soil_layered_info_df.loc[row, 'SLBS'], 6, decimal=3)
            SLPA  = formatInput(soil_layered_info_df.loc[row, 'SLPA'], 6, decimal=3)
            SLPB  = formatInput(soil_layered_info_df.loc[row, 'SLPB'], 6, decimal=3)
            SLKE  = formatInput(soil_layered_info_df.loc[row, 'SLKE'], 6, decimal=3)
            SLMG  = formatInput(soil_layered_info_df.loc[row, 'SLMG'], 6, decimal=3)
            SLNA  = formatInput(soil_layered_info_df.loc[row, 'SLNA'], 6, decimal=3)
            SLSU  = formatInput(soil_layered_info_df.loc[row, 'SLSU'], 6, decimal=3)
            SLEC  = formatInput(soil_layered_info_df.loc[row, 'SLEC'], 6, decimal=3)
            SLCA  = formatInput(soil_layered_info_df.loc[row, 'SLCA'], 6, decimal=3)
            text = text + ''.join([SLB,  SLPX, SLPT, SLPO, CACO3, SLAL, SLFE, SLMN, 
                                SLBS, SLPA, SLPB, SLKE, SLMG, SLNA, SLSU, SLEC,
                                SLCA])+'\n'
        
        text = text + headertext_list[3]
        for row in range(soil_layered_info_df.shape[0]):
            SLB   = formatInput(soil_layered_info_df.loc[row,  'SLB'], 6)
            ALFVG = formatInput(soil_layered_info_df.loc[row,'ALFVG'], 6, decimal=3)
            NVG   = formatInput(soil_layered_info_df.loc[row,  'NVG'], 6, decimal=3)
            MVG   = formatInput(1-(1/float(NVG)), 6, decimal=3)
            # MVG   = formatInput(soil_layered_info_df.loc[row,  'MVG'], 6, decimal=3)
            WCRES = formatInput(soil_layered_info_df.loc[row,'WCRES'], 6, decimal=3)
            text = text + ''.join([SLB,  ALFVG, MVG, NVG, WCRES])+'\n'
    elif 'SLPX' in soil_layered_info_df.columns:
        text = text + headertext_list[2]
        for row in range(soil_layered_info_df.shape[0]):
            SLB   = formatInput(soil_layered_info_df.loc[row,  'SLB'], 6)
            SLPX  = formatInput(soil_layered_info_df.loc[row, 'SLPX'], 6, decimal=1)
            SLPT  = formatInput(soil_layered_info_df.loc[row, 'SLPT'], 6)
            SLPO  = formatInput(soil_layered_info_df.loc[row, 'SLPO'], 6, decimal=3)
            CACO3 = formatInput(soil_layered_info_df.loc[row,'CACO3'], 6, decimal=3)
            SLAL  = formatInput(soil_layered_info_df.loc[row, 'SLAL'], 6, decimal=3)
            SLFE  = formatInput(soil_layered_info_df.loc[row, 'SLFE'], 6, decimal=3)
            SLMN  = formatInput(soil_layered_info_df.loc[row, 'SLMN'], 6, decimal=3)
            SLBS  = formatInput(soil_layered_info_df.loc[row, 'SLBS'], 6, decimal=3)
            SLPA  = formatInput(soil_layered_info_df.loc[row, 'SLPA'], 6, decimal=3)
            SLPB  = formatInput(soil_layered_info_df.loc[row, 'SLPB'], 6, decimal=3)
            SLKE  = formatInput(soil_layered_info_df.loc[row, 'SLKE'], 6, decimal=3)
            SLMG  = formatInput(soil_layered_info_df.loc[row, 'SLMG'], 6, decimal=3)
            SLNA  = formatInput(soil_layered_info_df.loc[row, 'SLNA'], 6, decimal=3)
            SLSU  = formatInput(soil_layered_info_df.loc[row, 'SLSU'], 6, decimal=3)
            SLEC  = formatInput(soil_layered_info_df.loc[row, 'SLEC'], 6, decimal=3)
            SLCA  = formatInput(soil_layered_info_df.loc[row, 'SLCA'], 6, decimal=3)
            text = text + ''.join([SLB,  SLPX, SLPT, SLPO, CACO3, SLAL, SLFE, SLMN, 
                                SLBS, SLPA, SLPB, SLKE, SLMG, SLNA, SLSU, SLEC,
                                SLCA])+'\n'
    elif 'ALFVG' in soil_layered_info_df.columns:
        text = text + headertext_list[2]
        for row in range(soil_layered_info_df.shape[0]):
            SLB   = formatInput(soil_layered_info_df.loc[row,  'SLB'], 6)
            ALFVG = formatInput(soil_layered_info_df.loc[row,'ALFVG'], 6, decimal=3)
            # MVG   = formatInput(soil_layered_info_df.loc[row,  'MVG'], 6, decimal=3)
            NVG   = formatInput(soil_layered_info_df.loc[row,  'NVG'], 6, decimal=3)
            MVG   = formatInput(1-(1/float(NVG)), 6, decimal=3)
            WCRES = formatInput(soil_layered_info_df.loc[row,'WCRES'], 6, decimal=3)
            text = text + ''.join([SLB,  ALFVG, MVG, NVG, WCRES])+'\n'
    return text

'___________________ function to check param in *.SOL file ____________________'
def fix_missing_soil_param(
        soil_info_df: pd.DataFrame, soil_layered_info_df: pd.DataFrame
        ) -> list[pd.DataFrame]:
    """
    Check the soil_info_df and soil_layered_info_df for any missing soil parameters,
    if found, the function supplement the columns in the dataframes with `-99` values

    :param soil_layered_info_df: pandas dataframe, the third table in the 
                                 soil profile which contains layered soil 
                                 profile information
    :param         soil_info_df: pandas dataframe, the second table in the 
                                 soil profile which contains general soil 
                                 information
    :return: soil_info_df, soil_layered_info_df
    """
    soil_info_params = ['SCOM', 'SALB', 'SLU1', 'SLDR', 'SLRO', 
                        'SLNF', 'SLPF', 'SMHB', 'SMPX', 'SMKE']
    soil_layered_info_params_tier1 = [
        'SLB','SLMH','SLLL','SDUL','SSAT','SRGF','SSKS','SBDM','SLOC','SLCL',
        'SLSI','SLCF','SLNI','SLHW','SLHB','SCEC','SADC']
    soil_layered_info_params_tier2 = [
        'SLB','SLPX','SLPT','SLPO','CACO3','SLAL','SLFE','SLMN','SLBS','SLPA',
        'SLPB','SLKE','SLMG','SLNA','SLSU','SLEC','SLCA']
    soil_layered_info_params_tier3 = ['SLB','ALFVG','MVG','NVG','WCRES']
    
    for soil_param in soil_info_params:
        if not soil_param in soil_info_df.columns:
            soil_info_df[soil_param] = ['-99' for _ in range(len(soil_info_df))]

    for soil_param in soil_layered_info_params_tier1:
        if not soil_param in soil_layered_info_df.columns:
            soil_layered_info_df[soil_param] = \
                ['-99' for _ in range(len(soil_layered_info_df))]
    if 'SLPX' in soil_layered_info_df.columns:
        for soil_param in soil_layered_info_params_tier2:
            if not soil_param in soil_layered_info_df.columns:
                soil_layered_info_df[soil_param] = \
                    ['-99' for _ in range(len(soil_layered_info_df))]
    if 'ALFVG' in soil_layered_info_df.columns:
        for soil_param in soil_layered_info_params_tier3:
            if not soil_param in soil_layered_info_df.columns:
                soil_layered_info_df[soil_param] = \
                    ['-99' for _ in range(len(soil_layered_info_df))]

    return [soil_info_df, soil_layered_info_df]


'_______________________ function for update *.SOL file _______________________'

def update_soil_profile(soilFilePath: str, old_soil_profile: str, 
                        new_soil_profile: str):
    '''
    Create the update the *.SOL file with the new soil profile

    :param soil_layered_info_df: pandas dataframe, the third table in the 
                                 soil profile which contains layered soil 
                                 profile information
    :param         soil_info_df: pandas dataframe, the second table in the 
                                 soil profile which contains general soil 
                                 information
    :param      headertext_list: list of the text up to header of the second
                                  table and text of third table header
    
    :return None: But update the *.SOL file with new data
    '''
    with open(soilFilePath, 'r+') as fsoil:
        soil_text = ''
        for line in fsoil:
            soil_text = soil_text + line
        soil_text = soil_text.replace(old_soil_profile, new_soil_profile)
        fsoil.truncate(0)
    with open(soilFilePath, 'w') as fsoil:
        fsoil.write(soil_text)
    return None


'________________ function for update soil layered parameters _________________'

def update_soil_layer_param(soilFilePath: str, soil_id: str, param_name_list: list[str], 
                            param_values_list: list[list[float]]):
    '''
    Read the soil layered parameters in *.SOL file of the DSSAT
    
    :param     soilFilePath: Complete path to the soil file (*.SOL)
    :param          soil_id: Soil ID followed with an asterick sign (*)
    :param  param_name_list: List of parameters (str) to be changed
    :param param_value_list: List of parameters' layered information in the same
                             order as the param_name_list

    :return None: But update the *.SOL file with new soil layered info
    '''
    soil_info_df, soil_layered_info_df, soil_lines, old_soil_profile, \
                  headertext_list = read_soil_profile(soilFilePath, soil_id)
    soil_info_df, soil_layered_info_df = \
        fix_missing_soil_param(soil_info_df, soil_layered_info_df)
    
    for i, param_name in enumerate(param_name_list):
        if param_name in soil_layered_info_df.columns:
            soil_layered_info_df.loc[:, param_name] = param_values_list[i]      # type: ignore
        if param_name in soil_info_df.columns:
            soil_info_df.loc[:, param_name] = param_values_list[i]              # type: ignore
        
    new_soil_profile = create_soil_profile(soil_layered_info_df,
                                           soil_info_df, headertext_list)
    
    update_soil_profile(soilFilePath, old_soil_profile, new_soil_profile)

    return None
        

'=============================================================================='

# if __name__ == "__main__":
#     soil_file = r'C:\DSSAT47\Soil\SOIL.SOL'
#     soil_id = '*IB00000007'
#     soil_info_df, soil_layered_info_df, soil_lines, old_soil_profile, headertext \
#         = read_soil_profile(soil_file, soil_id)
#     soil_lines = read_soil_profile(soil_file, soil_id, OnlyText=True)
#     print(soil_lines)
#     soil_file = r'C:\Users\r.gupta\Local Storage\DSSAT Multiprocessing\DSSAT Input Files\SOIL1.SOL'
#     with open(soil_file,'w') as f:
#         f.write(soil_lines)                                                     # type: ignore
#     new_soil_profile = create_soil_profile(soil_layered_info_df, soil_info_df, headertext)
#     update_soil_profile(soil_file, old_soil_profile, new_soil_profile)