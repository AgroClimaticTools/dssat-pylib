# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: To run DSSAT and update DSSBatch.v47 based on exp. file

"""


'=============================================================================='

import subprocess
import pandas as pd
from datetime import date, datetime
from typing import Optional
from pathlib import Path


'========================= DSSAT Formatting Functions ========================='

def julianDay(anydate: date) -> str:
    """
    Calculates julian days from any date in python date format

    :param anydate: date in python date format datetime.date(yyyy, m, d)
    :return       : Julian day for the given date

    """    
    return anydate.strftime("%j")

def date2dssatDate(anydate: date) -> str: 
    """
    Converts a python date to dssat date format

    :param anydate: date in python date format datetime.date(yyyy, m, d)
    :return       : dssat date 2-digit year format in str

    """    
    return anydate.strftime("%y%j")

def dssatDate2date(dssatDate: str|int) -> date:
    """
    Converts a dssat date format to python date format

    :param dssatDate: dssat date 2-digit year format in str
    :return         : date in python date format datetime.date(yyyy, m, d)

    """
    pythonDate = datetime.strptime(str(dssatDate), '%y%j').date()
    return pythonDate


'========================== DSSAT Utility Functions ==========================='

'_________________________________ Run DSSAT __________________________________'

def run_dssat(ExpFilePath: str|Path, DSSAT_dir: str|Path, 
              selected_treatments: Optional[list[str]]=None, 
              command: str = 'DSCSM048.EXE Q DSSBatch.v48'):
    """
    Run the DSSAT model

    :param ExpFilePath: DSSAT X file complete path in str or Path
    :param   DSSAT_dir: DSSAT directory in str or Path

    """
    ExpFilePath = Path(ExpFilePath)
    DSSAT_dir = Path(DSSAT_dir)
    directory = ExpFilePath.parent
    v = DSSAT_dir.name[-2:]
    
    # Create DSSAT Batch File
    create_DSSBatch(ExpFilePath, selected_treatments, command)

    # Run model
    dssat_running = subprocess.Popen(command, shell=False,
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     cwd=ExpFilePath)
    
    stdout, stderr = dssat_running.communicate()
    # os.chdir(directory)
    # os.system(str(DSSAT_dir) + "\DSCSM0" + v+ '.EXE Q DSSBatch.v'+ v)           # type: ignore
    return None


'____________________________ Create DSSBatch File ____________________________'

def create_DSSBatch(ExpFilePath: str|Path, selected_treatments: Optional[list[str]]=None, 
                    command: str = 'DSCSM048.EXE Q DSSBatch.v48'):
    """
    Create DSSBatch file using DSSAT X file

    :param         ExpFilePath: DSSAT X file complete path in str or Path
    :param selected_treatments: Treatments selected from the X file in list
    :param             command: DSSAT command to run dssat, defaults to 
                                'DSCSM048.EXE Q DSSBatch.v48'
    :return: None

    """
    ExpFilePath = Path(ExpFilePath)
    ExpDir = ExpFilePath.parent
    ExpFile = ExpFilePath.name
    v = command.split('.EXE')[0][-2:]
    DSSBatchFile = ExpDir / ('DSSBatch.v'+v)
    
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
                if selected_treatments is not None and \
                treatments_text[9:33].strip() in selected_treatments:
                    TRTNO.append(treatments_text[:2])
                    SQ.append(treatments_text[2:4])
                    OP.append(treatments_text[4:6])
                    CO.append(treatments_text[6:8])
                    TNAME.append(treatments_text[9:33])
                else:
                    TRTNO.append(treatments_text[:2])
                    SQ.append(treatments_text[2:4])
                    OP.append(treatments_text[4:6])
                    CO.append(treatments_text[6:8])
                    TNAME.append(treatments_text[9:33])
    treatment_df = pd.DataFrame({'TRTNO' : TRTNO, 'SQ' : SQ,
                                 'OP': OP, 'CO': CO})
    batch_text = '$BATCH(%s)' % ('Sequence'.upper()) + '\n' + '!' + '\n'
    batch_text = batch_text + '@FILEX                                                                                        TRTNO     RP     SQ     OP     CO\n'
    
    for row in range(treatment_df.shape[0]):
        batch_text = ''.join([batch_text, 
                              ExpFile.ljust(94),
                              treatment_df.loc[row, 'TRTNO'].rjust(5), 
                              treatment_df.loc[row, 'OP'].rjust(7),
                              treatment_df.loc[row, 'SQ'].rjust(7),
                              treatment_df.loc[row, 'OP'].rjust(7),
                              treatment_df.loc[row, 'CO'].rjust(7),
                              '\n'])                                            # type: ignore
    with open(DSSBatchFile, 'w') as Fbatch:
        Fbatch.write(batch_text)
    return None


'_______________________________ Read DATA.CDE ________________________________'

def read_datacde(dssat_dir: str|Path) -> pd.DataFrame:
    """
    Read DSSAT codes from Data.CDE file

    :param dssat_dir: DSSAT directory in str or Path
    :return         : dataframe of Data.CDE
    
    """
    dssat_dir = Path(dssat_dir)
    with open(dssat_dir / 'DATA.CDE', 'r', errors='replace') as f:
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

# if __name__ == '__main__':
    # ExpFilePath = input('Full path to experiment file (*.SQX): ')
    # create_DSSBatch(ExpFilePath, crop='Potato', command='DSCSM047.EXE PTSUB047 B DSSBatch.v47')
    # print(ExpFilePath)
    # run_dssat(ExpFilePath)
    # outputFolder = r'C:\DSSAT47\Sequence\Test DSSAT_1'
    # extract_dssat_summary(outputFolder)
