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
from typing import Awaitable, Callable


class RunMaesWidget(QtWidgets.QWidget):
    lineEdit_triger_ch1          : QtWidgets.QLineEdit
    lineEdit_triger_ch2          : QtWidgets.QLineEdit

    pushButton_run               : QtWidgets.QPushButton
    checkBox_trig1               : QtWidgets.QCheckBox
    checkBox_trig2               : QtWidgets.QCheckBox
    gridLayout_meas              : QtWidgets.QGridLayout

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
            lvl2 = int(self.lineEdit_triger_ch2.text())
            if self.flags[self.trig1_flag]:
                lvl1 = int(self.lineEdit_triger_ch1.text())
                await self.mpp_cmd.set_level(ch=0, lvl=lvl1)
                await self.mpp_cmd.start_measure(on=1)
            elif not self.flags[self.trig1_flag] and not self.flags[self.trig2_flag]:
                await self.mpp_cmd.start_forced(ch=0, on=1)
            elif self.flags[self.trig1_flag]:
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





