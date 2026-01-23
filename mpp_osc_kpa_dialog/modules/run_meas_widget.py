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

try:    
    from util.async_task_manager import AsyncTaskManager
    from util.parsers import Parsers
    from modules.graph_widget import GraphWidget
    from util.filters_data import FiltersData
    from modules.measure_widget import MeasureWidget
except:
    from mpp_osc_kpa_dialog.util.async_task_manager import AsyncTaskManager
    from mpp_osc_kpa_dialog.util.parsers import Parsers
    from mpp_osc_kpa_dialog.modules.graph_widget import GraphWidget
    from mpp_osc_kpa_dialog.util.filters_data import FiltersData
    from mpp_osc_kpa_dialog.modules.measure_widget import MeasureWidget


class RunMaesWidget(QtWidgets.QWidget):
    lineEdit_triger_ch1          : QtWidgets.QLineEdit
    lineEdit_triger_ch2          : QtWidgets.QLineEdit

    pushButton_run_trig          : QtWidgets.QPushButton
    checkBox_trig1               : QtWidgets.QCheckBox
    checkBox_trig2               : QtWidgets.QCheckBox
    gridLayout_meas              : QtWidgets.QGridLayout

    def __init__(self, parent) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('run_meas_widget_bdk2.ui'), self) 
        self.parent = parent
        self.graph_widget: GraphWidget = self.parent.w_graph_widget  # type: ignore
        self.task_manager = AsyncTaskManager()
        self.parser = Parsers()
        self.fd = FiltersData()
        self.measure_widget = MeasureWidget()
        # --------------------- init mpp id --------------------- #
        self.modules_mpp = {'МПП-1': 4, 'МПП-2': 5, 'МПП-3': 6, 'МПП-4': 7,'МПП-5': 8, 'МПП-6': 9, 'МПП-7': 3}
        try:
            self.lineEdit_ID : QtWidgets.QLineEdit # for run_meas_widget_comm.ui
            self.id = int(self.lineEdit_ID.text())
        except Exception:
            self.comboBox_module_mpp : QtWidgets.QComboBox  # for run_meas_widget_bdk2.ui
            self.comboBox_module_mpp.addItems(self.modules_mpp.keys())
        # ====================================================== #
        # --------------------- init client --------------------- #
        try:
            self.modbus: ModbusStreamDecoder = self.parent.module_driver.modbus
        except Exception as e:
            logger.error(e)
        # ====================================================== #
        # --------------- init external functions --------------- #
        mpp_id: int = self.modules_mpp[self.comboBox_module_mpp.currentText()]
        self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.modbus, mpp_id)
        # ====================================================== #
        # --------------------- init flags --------------------- #
        self.start_meas_flag = False

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
        self.pushButton_run_trig.clicked.connect(self.pushButton_run_trig_handler)
        self.comboBox_module_mpp.currentIndexChanged.connect(self.comboBox_module_mpp_updater)

    
    def init_flags(self):
        for checkBox, flag in self.checkbox_flag_mapping.items():
            checkBox.setChecked(self.flags[flag])
            self._checkbox_flag_state(flag)
        for checkbox, flag_name in self.checkbox_flag_mapping.items():
            checkbox.clicked.connect(partial(self._flag_state_handler, flag=flag_name))

    def _checkbox_flag_state(self, flag: str):
        if flag == self.trig1_flag:
            self.lineEdit_triger_ch1.setEnabled(self.flags[flag])
        if flag == self.trig2_flag:
            self.lineEdit_triger_ch2.setEnabled(self.flags[flag])

    def _flag_state_handler(self, state: bool, flag: str):
        self.flags[flag] = state
        self._checkbox_flag_state(flag)

    @qasync.asyncSlot()
    async def pushButton_run_trig_handler(self) -> None:
        await self.pushButton_run_trig_flag_updater()
        if self.start_meas_flag:
            self.start_async_task_loop_request()
        else:
            self.task_manager.cancel_task("ACQ_task")
        
    async def pushButton_run_trig_flag_updater(self):
        self.start_meas_flag = not self.start_meas_flag
        if self.start_meas_flag:
            self.text_button_trig: str = self.pushButton_run_trig.text()
            self.pushButton_run_trig.setText("Остановить изм.")
        else:
            self.pushButton_run_trig.setText(self.text_button_trig)
            await self.mpp_cmd.start_measure(ch=0, state=0)
            await self.mpp_cmd.start_measure(ch=1, state=0)

    def comboBox_module_mpp_updater(self):
        mpp_id: int = self.modules_mpp[self.comboBox_module_mpp.currentText()]
        self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.modbus, mpp_id)

    def start_async_task_loop_request(self) -> None:
        ACQ_task: Callable[[], Awaitable[None]] = self.asyncio_ACQ_loop_request
        self.task_manager.create_task(ACQ_task(), "ACQ_task")

    async def _trig_start(self):
        bool_trg1, bool_trg2 = self.flags[self.trig1_flag], self.flags[self.trig2_flag]
        lvl1 = int(self.lineEdit_triger_ch1.text())
        lvl2 = int(self.lineEdit_triger_ch2.text())

        if (bool_trg1, bool_trg2) == (True, True):
            await self.mpp_cmd.set_level(ch=0, lvl=lvl1)
            await self.mpp_cmd.set_level(ch=1, lvl=lvl2)
            await self.mpp_cmd.start_measure(ch=0, state=1)
            await self.mpp_cmd.start_measure(ch=1, state=1)
        elif (bool_trg1, bool_trg2) == (True, False):
            await self.mpp_cmd.set_level(ch=0, lvl=lvl1)
            await self.mpp_cmd.set_level(ch=1, lvl=lvl2)
            await self.mpp_cmd.start_measure(ch=0, state=1)
            await self.mpp_cmd.start_measure(ch=1, state=1)
        elif (bool_trg1, bool_trg2) == (False, True):
            await self.mpp_cmd.set_level(ch=0, lvl=lvl1)
            await self.mpp_cmd.set_level(ch=1, lvl=lvl2)
            await self.mpp_cmd.start_measure(ch=0, state=1)
            await self.mpp_cmd.start_measure(ch=1, state=1)

    async def _forced_start(self):
        bool_trg1, bool_trg2 = self.flags[self.trig1_flag], self.flags[self.trig2_flag]
        if (bool_trg1, bool_trg2) == (False, True):
            await self.mpp_cmd.start_forced(ch=0)
        elif (bool_trg1, bool_trg2) == (True, False):
            await self.mpp_cmd.start_forced(ch=1)
        elif (bool_trg1, bool_trg2) == (False, False):
            await self.mpp_cmd.start_forced(ch=0)
            await self.mpp_cmd.start_forced(ch=1)

    async def asyncio_ACQ_loop_request(self) -> None:
            self.graph_widget.show()
            await self._trig_start()
            while 1:
                await self._forced_start()
                result_ch0: bytes = await self.mpp_cmd.read_oscill(ch=0)
                result_ch1: bytes = await self.mpp_cmd.read_oscill(ch=1)
                result_ch0_int: list[int] = await self.parser.mpp_pars_16b(result_ch0)
                result_ch1_int: list[int] = await self.parser.mpp_pars_16b(result_ch1)
                data_ch0, data_ch1 = await self._graph_widget_drawable(result_ch0_int, result_ch1_int)
                await self._measure_widget_updater(data_ch0[1], data_ch1[1])
                await self.pushButton_run_trig_flag_updater()
                break

    async def _graph_widget_drawable(self, data_ch0, data_ch1) -> tuple:
        try:
            out_data_ch0: tuple[list, list] = await self.graph_widget.gp_ch0.draw_graph(data_ch0)  # x, y
            out_data_ch1: tuple[list, list] = await self.graph_widget.gp_ch1.draw_graph(data_ch1)  # x, y
            return out_data_ch0, out_data_ch1
        except asyncio.exceptions.CancelledError:
            return [], []
        
    async def _measure_widget_updater(self, data_ch0: list, data_ch1: list):
        try:
            max: float = self.fd.filters['max()'](data_ch0)
            min: float  = self.fd.filters['min()'](data_ch0)
            pk = self.fd.filters['pk()'](data_ch0)
            self.measure_widget.update_widget_ca_a(max, min, pk)
            max: float  = self.fd.filters['max()'](data_ch1)
            min: float  = self.fd.filters['min()'](data_ch1)
            pk = self.fd.filters['pk()'](data_ch1)
            self.measure_widget.update_widget_ca_b(max, min, pk)
        except Exception as e:
            logger.error(e)




