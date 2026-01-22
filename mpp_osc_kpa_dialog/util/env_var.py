'''Описания всех переменных проекта
'''

class EnvironmentVar():
    REG_MPP_COMMAND                 = 0x0000
    REG_MPP_ISSUE_WAVEFORM          = 0x0009
    REG_MPP_HH                      = 0x000A
    REG_GET_MPP_STRUCT              = 0x0006
    REG_MPP_HIST_32                 = 0x0014
    REG_MPP_HIST_16                 = 0x0020
    REG_MPP_HIST_HCP                = 0x0026
    REG_MPP_LEVEL                   = 0x0079
    REG_CALIBR_ALL_CH               = 0x0050
    REG_OSCILL_CH0                  = 0xA000
    REG_OSCILL_CH1                  = 0xA200

    

    MPP_LEVEL_TRIG                  = 0x0001
    MPP_TRIG_CNT_CLEAR              = 0x000B

    MPP_START_MEASURE: list[int]    = [0x0002, 0x0001]
    MPP_STOP_MEASURE: list[int]     = [0x0002, 0x0000]
    
    MPP_START_MEASURE_FORCED        = 0x0051


    def __init__(self):
        pass