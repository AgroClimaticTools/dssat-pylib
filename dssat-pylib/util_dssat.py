# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: To run DSSAT and update DSSBatch.v47 based on exp. file

"""


'=============================================================================='

import os
import pandas as pd
from datetime import date, timedelta


'========================= DSSAT Formatting Functions ========================='

def julianDay(anydate): 
    return str((anydate - date(int(anydate.year), 1, 1)).days + 1)

def date2dssatDate(anydate): 
    return str(int(anydate.year))[-2:] + julianDay(anydate).zfill(3)

def dssatDate2date(dssatDate):
    yy = dssatDate[:2]
    julianDay = int(dssatDate[2:])
    if int(yy) >= 86:
        year = int('19'+yy)
        return date(year, 1, 1)+timedelta(julianDay-1)
    else:
        year = int('20'+yy)
        return date(year, 1, 1)+timedelta(julianDay-1)


'========================== DSSAT Utility Functions ==========================='

'_________________________________ Run DSSAT __________________________________'

def run_dssat(ExpFilePath):
    splited_path = ExpFilePath.split('//')
    sep = '//'
    if len(splited_path) == 1:
        splited_path = ExpFilePath.split('\\')
        sep = '\\'
    try:
        directory = sep.join(splited_path[:-1])
        os.chdir(directory)
        os.system('/projects/aces/rishabh7/Data/DSSAT47/dscsm047 Q DSSBatch.v47')
    except:
        DSSATFolder = sep.join(splited_path[:2])
        directory = sep.join(splited_path[:-1])
        v = DSSATFolder[-2:]
        os.chdir(directory)
        os.system(DSSATFolder + "\DSCSM0" + v+ '.EXE Q DSSBatch.v'+ v)          # type: ignore


'____________________________ Create DSSBatch File ____________________________'

def create_DSSBatch(ExpFilePath: str, crop: str = 'Sequence', 
                    command: str = 'DSCSM047.EXE Q DSSBatch.v47'):
    
    splited_path = ExpFilePath.split('//')
    sep='//'
    if len(splited_path) == 1:
        splited_path = ExpFilePath.split('\\')
        sep='\\'
    
    ExpDir = sep.join(splited_path[:-1])
    ExpFile = splited_path[-1]
    cmd_line = ExpDir + sep + command
    v = command.split('.EXE')[0][-2:]
    DSSBatchFile = sep.join(splited_path[:-1] + ['DSSBatch.v'+v])
    
    treatments_text = ''
    TRTNO, SQ, OP, CO, TNAME = [], [], [], [], []
    with open(ExpFilePath) as Fexp:
        param = 0
        for line in Fexp.readlines():
            if line.startswith('@N R O C TNAME...'):
                param = 1
                continue
            if param == 1 and line.startswith('\n'):
                break
            if param == 1:
                treatments_text = line
                TRTNO.append(treatments_text[:2])
                SQ.append(treatments_text[2:4])
                OP.append(treatments_text[4:6])
                CO.append(treatments_text[6:8])
                TNAME.append(treatments_text[9:33])
    treatment_df = pd.DataFrame({'TRTNO' : TRTNO, 'SQ' : SQ,
                                 'OP': OP, 'CO': CO})
    directory = ExpDir
    batch_text = '$BATCH(%s)' % ('Sequence'.upper()) + '\n' + '!' + '\n'
    batch_text = batch_text + '! Directory    : %s' % (directory) + '\n'  
    batch_text = batch_text + '! Command Line : %s' % (cmd_line) + '\n'
    batch_text = batch_text + '! Crop         : %s' % (crop) + '\n'
    batch_text = batch_text + '! Experiment   : %s' % (ExpFile) + '\n'
    batch_text = batch_text + '! ExpNo        : 1' + '\n'
    batch_text = batch_text + '! Debug        : %s' % (cmd_line) + '\n' + '!' + '\n'
    batch_text = batch_text + '@FILEX                                                                                        TRTNO     RP     SQ     OP     CO\n'
    
    for row in range(treatment_df.shape[0]):
        batch_text = batch_text + ExpFile.ljust(94) + \
            treatment_df.loc[row, 'TRTNO'].rjust(5) + \
            treatment_df.loc[row, 'OP'].rjust(7) + \
            treatment_df.loc[row, 'SQ'].rjust(7) + \
            treatment_df.loc[row, 'OP'].rjust(7) + \
            treatment_df.loc[row, 'CO'].rjust(7) + '\n'
    with open(DSSBatchFile, 'w') as Fbatch:
        Fbatch.write(batch_text)
    return None


'_______________________________ Read DATA.CDE ________________________________'

def read_datacde(dssat_dir):
    with open(dssat_dir+'//DATA.CDE', 'r') as f:
        lines = f.readlines()
        data = []
        for line in lines:
            if not line[0] in ['\n','@','!','*']:
                cde         = line[:7].strip()
                label       = line[7:23].strip()
                description = line[23:80].strip()
                data.append([cde, label, description])
    df = pd.DataFrame(data, columns=['CDE', 'LABEL', 'DESCRIPTION'])
    df = df.set_index('CDE')
    return df

if __name__ == '__main__':
    # ExpFilePath = input('Full path to experiment file (*.SQX): ')
    ExpFilePath = r'C:\Users\r.gupta\OneDrive - University of Florida\pyFunc\pyDSSAT\Testing\AIHA1302.PTX'
    create_DSSBatch(ExpFilePath, crop='Potato', command='DSCSM047.EXE PTSUB047 B DSSBatch.v47')
    # print(ExpFilePath)
    # run_dssat(ExpFilePath)
    # outputFolder = r'C:\DSSAT47\Sequence\Test DSSAT_1'
    # extract_dssat_summary(outputFolder)
