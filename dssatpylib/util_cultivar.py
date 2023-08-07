# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: To update corn, soybean, and potato cultivars in *.CUL file

"""
from typing import Optional, Union

def update_corn_cultivar(param: Union[str,dict], 
    cul_srcdir: str, cul_dstdir: str) -> None:
    'param can be dictionary of parameters or '
    'simply a string with all the parameters in DSSAT format'

    f_MZCER048_CUL_SRC = cul_srcdir+'//MZCER048.CUL'
    f_MZCER048_CUL_DST = cul_dstdir+'//MZCER048.CUL'

    with open(f_MZCER048_CUL_SRC, 'r') as f:
        CUL_Line = f.readlines()
    if type(param) is dict:
        param_dict = param
        Var = param_dict['VAR']
        VarName = ' ' + param_dict['VRNAME']
        Eco = '. ' + param_dict['ECO#']
        P1 = ' ' + str('%.1f' % param_dict['P1'])
        P2 = ' ' + str('%.3f' % param_dict['P2'])
        P5 = ' ' + str('%.1f' % param_dict['P5'])
        G2 = ' ' + str('%.1f' % param_dict['G2'])
        G3 = '  ' + str('%.2f' % param_dict['G3'])
        PhInt = ' ' + str('%.2f' % param_dict['PHINT'])

        if len(VarName) > 22:
            VarName = VarName[:22]
        else:
            VarName = VarName.ljust(22)
        CUL_Details = Var + VarName + Eco + P1 + P2 + P5 + G2 + G3 + PhInt

    elif type(param) is str:
        CUL_Details = param
    else:
        return None

    for i, line in enumerate(CUL_Line):
        if CUL_Details[:6] in line:
            lineIndex2Update = i
    else:
        lineIndex2Update = len(CUL_Line)
    if lineIndex2Update < len(CUL_Line):
        CUL_Line[lineIndex2Update] = CUL_Details
    else:
        CUL_Line.append('\n'+CUL_Details)

    with open(f_MZCER048_CUL_DST, 'w') as file:
        file.writelines(CUL_Line)
    
    return None


def update_soybean_cultivar(param: Union[str,dict], 
        cul_srcdir: str, cul_dstdir: str) -> None:
    'param can be dictionary of parameters or '
    'simply a string with all the parameters in DSSAT format'
    
    f_SBGRO048_CUL_SRC = cul_srcdir+'SBGRO048.CUL'
    f_SBGRO048_CUL_DST = cul_dstdir+'SBGRO048.CUL'
    with open(f_SBGRO048_CUL_SRC, 'r') as f:
        CUL_Line = f.readlines()
    if type(param) is dict:
        param_dict = param
        Var = param_dict['VAR']
        VarName = ' ' + param_dict['VRNAME']
        Eco = '. ' + param_dict['ECO#']
        CSDL = ' ' + str('%.2f' % param_dict['CSDL'])
        PPSEN = ' ' + str('%.3f' % param_dict['PPSEN'])
        EM_FL = '  ' + str('%.1f' % param_dict['EM-FL'])
        FL_SH = '  ' + str('%.1f' % param_dict['FL-SH']).rjust(4)
        FL_SD = '  ' + str('%.1f' % param_dict['FL-SD'])
        SD_PM = ' ' + str('%.2f' % param_dict['SD-PM'])
        FL_LF = ' ' + str('%.2f' % param_dict['FL-LF'])
        LFMAX = ' ' + str('%.3f' % param_dict['LFMAX'])
        SLAVR = '  ' + str('%.0f' % param_dict['SLAVR']) + '.'
        SIZLF = ' ' + str('%.1f' % param_dict['SIZLF'])
        XFRT = '  ' + str('%.2f' % param_dict['XFRT'])
        WTPSD = '  ' + str('%.2f' % param_dict['WTPSD'])
        SFDUR = '  ' + str('%.1f' % param_dict['SFDUR'])
        SDPDV = '  ' + str('%.2f' % param_dict['SDPDV'])
        PODUR = '  ' + str('%.1f' % param_dict['PODUR'])
        THRSH = '  ' + str('%.1f' % param_dict['THRSH'])
        SDPRO = '  ' + str('%.3f' % param_dict['SDPRO'])[1:]
        SDLIP = '  ' + str('%.3f' % param_dict['SDLIP'])[1:]

        if len(VarName) > 22:
            VarName = VarName[:22]
        else:
            VarName = VarName.ljust(22)

        CUL_Details1 = Var + VarName + Eco + CSDL + \
            PPSEN + EM_FL + FL_SH + FL_SD + SD_PM
        CUL_Details2 = FL_LF + LFMAX + SLAVR + SIZLF + XFRT + WTPSD + SFDUR
        CUL_Details3 = SDPDV + PODUR + THRSH + SDPRO + SDLIP

        CUL_Details = CUL_Details1 + CUL_Details2 + CUL_Details3
    elif type(param) is str:
        CUL_Details = param
    else:
        return None

    for i, line in enumerate(CUL_Line):
        if CUL_Details[:6] in line:
            lineIndex2Update = i
    else:
        lineIndex2Update = len(CUL_Line)
    if lineIndex2Update < len(CUL_Line):
        CUL_Line[lineIndex2Update] = CUL_Details
    else:
        CUL_Line.append('\n'+CUL_Details)

    with open(f_SBGRO048_CUL_DST, 'w') as file:
        file.writelines(CUL_Line)
    return None



def update_potato_cultivar(param: Union[str,dict], 
        cul_dstdir: str, cul_srcdir: Optional[str] = None) -> None:
    '''
    Update the genotype coeficients in potato cultivar
    
    :param dict/str: genotype coeficients in potato cultivar 
                     param can be dictionary of parameters or 
                     simply a string with all the parameters in DSSAT format
    :cul_dstdir str: destination where *.CUL file get stored, can be same as 
                     cul_dstdir to update the *.CUL file at cul_srcdir
    :cul_srcdir str: default None, source directory where *.CUL file is stored.
                     If cul_srcdir and cul_dstdir are different, function will
                     create a new file with update genotype coef. at cul_dstdir.
                     If cul_srcdir and cul_dstdir are same, function will
                     update file at cul_srcdir with new genotype coef.

    :return         : None
    '''
    
    if cul_srcdir is None:
        CUL_Line = ['*POTATO CULTIVAR COEFFICIENTS: PTSUB048 MODEL\n',
            '\n@VAR#  VAR-NAME........ EXPNO   ECO#    G2    G3    PD    P2    TC\n']
    else:
        f_PTSUB048_CUL_SRC = cul_srcdir+'\\PTSUB048.CUL'
        with open(f_PTSUB048_CUL_SRC, 'r') as f:
            CUL_Line = f.readlines()
        
    f_PTSUB048_CUL_DST = cul_dstdir+'\\PTSUB048.CUL'

    if type(param) is dict:
        param_dict = param
        Var = param_dict['VAR']
        VarName = param_dict['VRNAME']
        Eco = '. ' + param_dict['ECO#']
        G2 = str('%.1f' % param_dict['G2'])[:-1]
        G3 = str('%.1f' % param_dict['G3'])
        PD = str('%.1f' % param_dict['PD'])
        P2 = str('%.1f' % param_dict['P2'])
        TC = str('%.1f' % param_dict['TC'])
        if len(VarName) > 20:
            VarName = VarName[:20]
        else:
            VarName = VarName.ljust(20)
        
        CUL_Details = '{:<5} {:>20} {:>8} {:>5}  {:>4}   {:>3}   {:>3}  {:>4}'.format(
            Var, VarName, Eco, G2, G3, PD, P2, TC)
    elif type(param) is str:
        CUL_Details = param
    else:
        return None
    
    for i, line in enumerate(CUL_Line):
        if CUL_Details[:6] in line:
            lineIndex2Update = i
    else:
        lineIndex2Update = len(CUL_Line)
    if lineIndex2Update < len(CUL_Line):
        CUL_Line[lineIndex2Update] = CUL_Details
    else:
        CUL_Line.append('\n'+CUL_Details)
    with open(f_PTSUB048_CUL_DST, 'w') as file:
        file.writelines(CUL_Line)

if __name__ == '__main__':
    param = {
        "VAR" : 'HA0001',
        "VRNAME" : 'AT-MODIFIED',
        "ECO#" : 'IB0001',
        "G2" : 900.,
        "G3" : 21.0,
        "PD" : 0.8,
        "P2" : 0.6,
        "TC" : 15.0
    }
    # cul_srcdir = r'C:\Users\r.gupta\Desktop'
    cul_dstdir = r'C:\Users\r.gupta\Desktop'
    update_potato_cultivar(param, cul_dstdir)