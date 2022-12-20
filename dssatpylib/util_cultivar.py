# -*- coding: utf-8 -*-
"""
Created by: Rishabh Gupta

Description: To update corn and soybean cultivars in *.CUL file

"""

def update_corn_cultivar(param, cul_srcdir, cul_dstdir):
    'param can be dictionary of parameters or '
    'simply a string with all the parameters in DSSAT format'

    f_MZCER047_CUL_SRC = cul_srcdir+'//MZCER047.CUL'
    f_MZCER047_CUL_DST = cul_dstdir+'//MZCER047.CUL'

    with open(f_MZCER047_CUL_SRC) as f:
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
    
    elif type(param) is str:
        CUL_Details = param
    else:
        return None

    CUL_Details = Var + VarName + Eco + P1 + P2 + P5 + G2 + G3 + PhInt

    CUL_Line[len(CUL_Line)-1] = CUL_Details

    with open(f_MZCER047_CUL_DST, 'w') as file:
        file.writelines(CUL_Line)
    
    return None


def update_soybean_cultivar(param, cul_srcdir, cul_dstdir):
    'param can be dictionary of parameters or '
    'simply a string with all the parameters in DSSAT format'
    
    f_SBGRO047_CUL_SRC = cul_srcdir+'SBGRO047.CUL'
    f_SBGRO047_CUL_DST = cul_dstdir+'SBGRO047.CUL'
    with open(f_SBGRO047_CUL_SRC) as f:
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

    CUL_Line[len(CUL_Line)-1] = CUL_Details

    with open(f_SBGRO047_CUL_DST, 'w') as file:
        file.writelines(CUL_Line)
    return None
