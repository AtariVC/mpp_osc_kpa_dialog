'''Постоянные проекта 
'''

class EnvironmentVar():
    MPP_CTRL                        = 0x0000  # Для записи команд

    MPP_SET_LEVEL                   = 0x0001  # установить уровень регистрации помехи = Params[0]
    MPP_START_MEASURE               = 0x0002  # запустить/остановить процесс регистрации (Params[0] == 0 - остановить)
    MPP_GET_N_NOISE                 = 0x0003  # выбрать оперативные помехи в кол-ве Params[0] штук
    MPP_GET_N_LIFETIME_NOISE        = 0x0004  # выбрать помехи с наибольшим LifeTime в кол-ве Params[0] штук
    MPP_GET_N_NEW_NOISE             = 0x0005  # выбрать самые свежие помехи в кол-ве Params[0] штук
    MPP_GET_N_OLD_NOISE             = 0x0006  # выбрать самые старые помехи в кол-ве Params[0] штук
    MPP_GET_N_NOISE_IN_INTERVAL     = 0x0007  # выбрать помехи в интервале от [Params[1]:Params[2]]сек.(вкл.) до [Params[3]:Params[4]]сек.(искл.)

    MPP_SET_WINDOW_NOISE            = 0x0010  # установить границы окон в кол-ве 3-х штук: Params[0], Params[1], Params[2] для выбранного канала
    MPP_CALIBR_ALL_CH               = 0x0050  # выполнить самокалибровку всех каналов
    MPP_FORCED_START                = 0x0051  # принудительный запуск цикла регистрации
    MPP_READ_EEPROM                 = 0x0052  # читать из EEPROM-a UintLeng байт (max 128) 
                                              # по адресу [Params[1]:Params[2]] в VUnit (номер канала памяти определяется адресом)
    MPP_WRITE_EEPROM                = 0x0053  # записать в EEPROM UintLeng байт (max 128) 
                                              #по адресу [Params[1]:Params[2]] из VUnit (номер канала памяти определяется адресом)
    MPP_CLEAR_ARCHIVE_MEM           = 0x0054  # очистить архивную память (номер канала памяти определяется Ctrl[15:8]
    MPP_CONST_MODE                  = 0x00FF  # режим констант (Params[0] == 1 - включить)

    # reg
    MPP_REG_CURRENT_MEAN_CH0        = 111
    MPP_REG_CURRENT_MEAN_CH1        = 112
    MPP_REG_CURRENT_NOISE_CH0       = 113
    MPP_REG_CURRENT_NOISE_CH1       = 114
    MPP_REG_LVL_CH0                 = 121
    MPP_REG_LVL_CH1                 = 122

    MPP_REG_OSCILL_CH0              = 0xA000  # регистры чтения осциллограмм ch1
    MPP_REG_OSCILL_CH1              = 0xA200  # регистры чтения осциллограмм ch2


    def __init__(self):
        pass