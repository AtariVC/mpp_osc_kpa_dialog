from PyQt6 import QtWidgets, QtCore
from qtpy.uic import loadUi
from qasync import asyncSlot
import asyncio
import qtmodern.styles
import sys
import qasync
# from save_config import ConfigSaver
from pathlib import Path
import struct
import crc16

####### импорты из других директорий ######
# /src
src_path = Path(__file__).resolve().parent.parent.parent.parent
modules_path = Path(__file__).resolve().parent.parent.parent
# Добавляем папку src в sys.path
sys.path.append(str(src_path))
sys.path.append(str(modules_path))

from modbus_worker import ModbusWorker                          # noqa: E402
# from parsers import  Parsers                                    # noqa: E402
from ddii_command import ModbusCMCommand, ModbusMPPCommand      # noqa: E402

MB_READ = 0x06

class RunMaesWidget(QtWidgets.QDialog):
    lineEdit_triger_ch1                 : QtWidgets.QLineEdit
    lineEdit_triger_ch2                 : QtWidgets.QLineEdit
    lineEdit_ID                         : QtWidgets.QLineEdit

    pushButton_run                      : QtWidgets.QPushButton
    pushButton_forced_meas              : QtWidgets.QPushButton
    checkBox_enable_test_csa            : QtWidgets.QCheckBox

    pushButton_forced_meas_signal       = QtCore.pyqtSignal()
    pushButton_run_signal               = QtCore.pyqtSignal()
    # checkBox_enable_test_csa_signal     = QtCore.pyqtSignal()


    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('WidgetRunMeasure.ui'), self)
        self.mw = ModbusWorker()
        self.status_forced_meas = 0
        self.status_run = 0
        # self.parser = Parsers()
        self.task = None # type: ignore
      # if __name__ != "__main__":
            # self.client = args[0]
            # self.logger = args[1]
            # self.cm_cmd: ModbusCMCommand = ModbusCMCommand(self.client, self.logger)
            # self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.client, self.logger)
        # self.pushButton_autorun.clicked.connect(self.pushButton_autorun_handler)
        # self.checkBox_enable_test_csa.clicked.connect(self.checkBox_enable_test_csa_handler)
        self.pushButton_run.clicked.connect(self.pushButton_run_handler)
        self.pushButton_forced_meas.clicked.connect(self.pushButton_forced_meas_handler)

    # def pushButton_autorun_handler(self) -> None:
    #     self.pushButton_autorun_signal.emit()

    # def checkBox_enable_test_csa_handler(self, state) -> None:
    #     print(state)

    @asyncSlot()
    def pushButton_run_handler(self) -> None:
        self.status_forced_meas = 0
        self.status_run = 1
        self.creator_task()


    def pushButton_forced_meas_handler(self):
        self.status_forced_meas = 1
        self.status_run = 0
        self.creator_task()

    def creator_task(self) -> None:
        try:
            if self.task is None or self.task.done():
                self.task: asyncio.Task[None] = asyncio.create_task(self.asyncio_loop_request_chs())
        except Exception as e:
            print(e)

    @asyncSlot()
    async def asyncio_loop_request_chs(self) -> None:
        try:
            while 1:
                if self.status_forced_meas == 1 and self.status_forced_meas == 0:
                    addr         = int(self.lineEdit_ID.text())
                    cmd_code     = MB_READ
                    read_amount  = 64
                    first_reg    = 0x1408 #?
                    for (): # вычитываем по 64 байта
                        # установить триггер
                        # начать измерение
                        self._gen_modbus_packet(addr, cmd_code, read_amount, first_reg)
                        self.send_uart
                        # перехватить данные и отправить в функцию построения графика
                elif self.status_forced_meas == 0 and self.status_forced_meas == 1:
                    for (): # вычитываем по 64 байта
                        await self._gen_modbus_packet()
                        self.send_uart
                else:
                    break
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            ...

    def _gen_modbus_packet(self, addr, cmd_code, read_amount, first_reg):
        def read_regs() -> bytes:
            data: bytes = struct.pack('>BBHH', addr, cmd_code, first_reg,
                                      read_amount)
            data += struct.pack('>BB' , *crc16.crc16(data))
            return data
        def write_reg() -> bytes:
            data: bytes = struct.pack(f'>BBH{len(tx_data)}s', addr, cmd_code,
                                      first_reg, tx_data)
            data += struct.pack('>BB' , *crc16.crc16(data))
            return data
        # def write_regs() -> bytes:
        #     reg_amount: int = len(tx_data) // 2
        #     data: bytes = struct.pack(f'>BBHHB{len(tx_data)}s', addr, cmd_code,
        #                               first_reg, reg_amount, len(tx_data),
        #                               tx_data)
            # data += struct.pack('>BB' , *crc16.crc16(data))
            # return data
        if cmd_code in [0x01, 0x02, 0x03, 0x04]:
            return read_regs()
        elif cmd_code in [0x05, 0x06]:
            return write_reg()
        else:
            return write_regs()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)
    w = RunMaesWidget()
    event_loop = qasync.QEventLoop(app)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    w.show()

    if event_loop:
        try:
            event_loop.run_until_complete(app_close_event.wait())
        except asyncio.CancelledError:
            ...



