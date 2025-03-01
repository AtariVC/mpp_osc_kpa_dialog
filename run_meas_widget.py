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


######### Для встраивания в KPA #############
try:
    from kpa_parser.modbus_frame import crc16
except ImportError:
    pass
######### Для отдельного запуска модуля #############



####### импорты из других директорий ######
# /src
# src_path = Path(__file__).resolve().parent.parent.parent.parent
# modules_path = Path(__file__).resolve().parent.parent.parent
# # Добавляем папку src в sys.path
# sys.path.append(str(src_path))
# sys.path.append(str(modules_path))

# from modbus_worker import ModbusWorker                            # noqa: E402
# # from parsers import  Parsers                                    # noqa: E402
# from ddii_command import ModbusCMCommand, ModbusMPPCommand        # noqa: E402


class RunMaesWidget(QtWidgets.QDialog):
    lineEdit_triger_ch1          : QtWidgets.QLineEdit
    lineEdit_triger_ch2          : QtWidgets.QLineEdit
    pushButton_run_trig_pips     : QtWidgets.QPushButton
    pushButton_autorun           : QtWidgets.QPushButton
    pushButton_forced_meas       : QtWidgets.QPushButton
    checkBox_enable_test_csa     : QtWidgets.QCheckBox
    gridLayout_meas              : QtWidgets.QGridLayout
    lineEdit_ID                  : QtWidgets.QLineEdit


    pushButton_autorun_signal           = QtCore.pyqtSignal()
    pushButton_run_trig_pips_signal     = QtCore.pyqtSignal()
    # checkBox_enable_test_csa_signal     = QtCore.pyqtSignal()

    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('WidgetRunMeasure.ui'), self)
        # self.mw = ModbusWorker()
        # self.parser = Parsers()
        self.task = None
        # self.client = args[0]
        if __name__ != "__main__":
            # self.client = args[0]
            # self.logger = args[1]
            # self.cm_cmd: ModbusCMCommand = ModbusCMCommand(self.client, self.logger)
            # self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.client, self.logger)
            pass
        try:
            self.client = args[0]
            print(self.client)
        except:
            pass
        # self.pushButton_autorun.clicked.connect(self.pushButton_autorun_handler)
        self.pushButton_run_trig_pips.clicked.connect(self.pushButton_run_trig_pips_handler)
        self.pushButton_forced_meas.clicked.connect(self.pushButton_forced_meas_handler)
        # self.checkBox_enable_test_csa.clicked.connect(self.checkBox_enable_test_csa_handler)

    # def pushButton_autorun_handler(self) -> None:
    #     self.pushButton_autorun_signal.emit()

    def pushButton_run_trig_pips_handler(self) -> None:
        self.pushButton_run_trig_pips_signal.emit()
        # self.

    # def checkBox_enable_test_csa_handler(self, state) -> None:
    #     print(state)

    def pushButton_forced_meas_handler(self):
        try:
            self.pushButton_run_trig_pips_signal.emit()
            addr = self.lineEdit_ID.value()
            cmd_code = 16
            read_amount = 64
            first_reg = 0
            data: bytes = struct.pack('>BBHH', addr, cmd_code, first_reg,
                                      read_amount)
            data += struct.pack('>BB' , *crc16.crc16(data))
            self.client._gen_modbus_packet(addr, cmd_code, read_amount, first_reg, tx_data)
        except Exception as e:
            print(e)


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



