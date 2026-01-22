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
from loguru import logger
from kpa_async_driver.module_driver import Module_Driver
from util.command_interface import ModbusMPPCommand
from kpa_async_driver.modbus_stream.stream_decoder import ModbusStreamDecoder
from functools import partial


######### Для встраивания в KPA #############
# try:
#     from kpa_async_bdk2m_pyqt.kpa_gui_model import KPA_BDK2_GUI_Model
#     # from kpa_parser.modbus_frame import crc16
#     # from kpa_parser.modbus_frame.packet_types import ModbusFrame
#     # from kpa_parser.modbus_frame.stream_decoder import ModbusStreamDecoder
#     # from kpa_async_pyqt_client.internal_bus.graph_widget.plot_renderer import GraphPen
#     # from kpa_async_pyqt_client.internal_bus.graph_widget.graph_widget import GraphWidget
# except ImportError:
#     pass
######### Для отдельного запуска модуля #############

# define
AMNT_RD_RG = 64

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


class RunMaesWidget(QtWidgets.QWidget):
    lineEdit_triger_ch1          : QtWidgets.QLineEdit
    lineEdit_triger_ch2          : QtWidgets.QLineEdit
    # pushButton_run_trig_pips     : QtWidgets.QPushButton
    pushButton_run               : QtWidgets.QPushButton
    checkBox_trig1               : QtWidgets.QCheckBox
    checkBox_trig2               : QtWidgets.QCheckBox
    gridLayout_meas              : QtWidgets.QGridLayout

    # lineEdit_ID                  : QtWidgets.QLineEdit # for run_meas_widget_comm.ui
    # comboBox_module_mpp          : QtWidgets.QComboBox  # for run_meas_widget_bdk2.ui

    # pushButton_autorun_signal           = QtCore.pyqtSignal()
    # pushButton_run_trig_pips_signal     = QtCore.pyqtSignal()
    # checkBox_enable_test_csa_signal     = QtCore.pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('run_meas_widget_bdk2.ui'), self) 
        self.parent = parent
        self.graph_widget: GraphWidget = self.parent.w_graph_widget  # type: ignore
        # --------------------- init mpp id --------------------- #
        modules_mpp = {'МПП-1': 4, 'МПП-2': 5, 'МПП-3': 6, 'МПП-4': 7,'МПП-5': 8, 'МПП-6': 9, 'МПП-7': 3}
        try:
            self.lineEdit_ID : QtWidgets.QLineEdit # for run_meas_widget_comm.ui
            self.id = int(self.lineEdit_ID.text())
        except Exception:
            self.comboBox_module_mpp : QtWidgets.QComboBox  # for run_meas_widget_bdk2.ui
            self.comboBox_module_mpp.addItems(modules_mpp.keys())
        # ====================================================== #
        # --------------------- init client --------------------- #
        try:
            self.modbus: ModbusStreamDecoder = self.parent.module_driver.modbus
        except Exception as e:
            logger.error(e)
        # ====================================================== #
        # --------------- init external functions --------------- #
        mpp_id: int = modules_mpp[self.comboBox_module_mpp.currentText()]
        self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.modbus, mpp_id)
        # ====================================================== #
        # --------------------- init flags --------------------- #
        self.trig1_flag: str = "trig1_flag"
        self.trig2_flag: str = "trig2_flag"

        self.flags = {
            self.trig1_flag: False,
            self.trig2_flag: False,
        }
        self.checkbox_flag_mapping = {
            self.checkBox_trig1: self.trig1_flag,
            self.checkBox_trig2: self.trig2_flag
        }
        self.init_flags()
        # ====================================================== #
        self.pushButton_run.clicked.connect(self.pushButton_run_handler)

    def init_flags(self):
        for checkBox, flag in self.checkbox_flag_mapping.items():
            checkBox.setChecked(self.flags[flag])
            self._checkbox_flag_state(flag)
        for checkbox, flag_name in self.checkbox_flag_mapping.items():
            checkbox.clicked.connect(partial(self.flag_state_handler, flag=flag_name))

    def _checkbox_flag_state(self, flag: str):
        if flag == self.trig1_flag:
            self.lineEdit_triger_ch1.setEnabled(self.flags[flag])
        if flag == self.trig2_flag:
            self.lineEdit_triger_ch2.setEnabled(self.flags[flag])

    def flag_state_handler(self, state: bool, flag: str):
        self.flags[flag] = state
        self._checkbox_flag_state(flag)

    def pushButton_run_handler(self) -> None:
        # self.pushButton_run_trig_pips_signal.emit()
        # self.
        pass

    def init_async_task_loop_request(self, ) -> None:
        ACQ_task: Callable[[], Awaitable[None]] = self.asyncio_ACQ_loop_request

    async def asyncio_ACQ_loop_request(self) -> None:
        try:
            lvl = int(self.lineEdit_trigger.text())
            save: bool = False
            if not self.w_ser_dialog.is_modbus_ready():
                await self._stop_measuring("Потеряно соединение")
                return
            if self.flags[self.enable_trig_meas_flag]:
                await self.mpp_cmd.set_level(lvl)
                await self.mpp_cmd.start_measure(on=1)
            self.graph_widget.show()
            while 1:




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



