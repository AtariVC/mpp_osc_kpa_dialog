from PyQt6 import QtWidgets, QtCore
from qtpy.uic import loadUi
from qasync import asyncSlot
import qasync
from PyQt6.QtWidgets import QGroupBox, QGridLayout, QSpacerItem, QSizePolicy, QWidget
from PyQt6.QtGui import QFont
import qtmodern.styles
import sys
from pymodbus.client import AsyncModbusSerialClient
import asyncio
from pathlib import Path
from typing import Dict
import sys
from loguru import logger

graph_widget_path = Path(__file__).parent
# Добавляем папку src в sys.path
sys.path.append(str(graph_widget_path))

######### Для встраивания в KPA #############
try:
    # from kpa_async_pyqt_client.internal_bus.graph_widget.modbus_worker import ModbusWorker
    # from kpa_async_pyqt_client.internal_bus.graph_widget.log_config import log_init
    from kpa_async_pyqt_client.internal_bus.graph_widget.tabWidget_maker import init_graph_window, create_tab_widget_items
    from kpa_async_pyqt_client.internal_bus.graph_widget.graph_widget import GraphWidget
    from kpa_async_pyqt_client.internal_bus.graph_widget.run_meas_widget import RunMaesWidget
except ImportError:
######### Для отладочного запуска через __main__ #############
    # from modbus_worker import ModbusWorker
    # from ddii_command import ModbusCMCommand, ModbusMPPCommand
    # from log_config import log_init
    from util.tabwidget_maker import init_graph_window, create_tab_widget_items
    from modules.graph_widget import GraphWidget
    from modules.run_meas_widget import RunMaesWidget


class MainGraphWidget(QtWidgets.QDialog):
    mainGridLayout                      : QtWidgets.QGridLayout

    coroutine_get_temp_finished = QtCore.pyqtSignal()

    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('main.ui'), self)
        try:
            self.client = args[0]
            self.run_widget: RunMaesWidget =  RunMaesWidget(self.client)
        except:
            self.run_widget: RunMaesWidget =  RunMaesWidget()
        graph_widget: GraphWidget = GraphWidget()
        osc_widgets =  {"Измерение": self.run_widget}
        widget_model: Dict[str, Dict[str, dict]] = {"Осциллограмма": osc_widgets}
        init_graph_window(self.mainGridLayout, graph_widget, widget_model)
        self.flg_get_rst = 0

        self.task = None # type: ignore




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)

    w: MainGraphWidget = MainGraphWidget()
    graph_widget: GraphWidget = GraphWidget()
    run_widget: RunMaesWidget =  RunMaesWidget()
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    w.show()

    with event_loop:
        try:
            event_loop.run_until_complete(app_close_event.wait())
        except asyncio.CancelledError:
            ...