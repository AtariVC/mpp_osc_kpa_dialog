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
from mpp_osc_kpa_dialog.util.main_window_maker import clear_left_widget, create_split_widget, create_tab_widget_items
from mpp_osc_kpa_dialog.modules.graph_widget import GraphWidget
from mpp_osc_kpa_dialog.modules.run_meas_widget import RunMaesWidget
from mpp_osc_kpa_dialog.modules.measure_widget import MeasureWidget

# verticalLayout_3

class MainGraphWidget(QtWidgets.QDialog):
    mainGridLayout                      : QtWidgets.QGridLayout

    coroutine_get_temp_finished = QtCore.pyqtSignal()

    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('main.ui'), self)
        self.init_widgets()
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

    def init_widgets(self) -> None:
        # Виджеты
        self.run_widget: RunMaesWidget =  RunMaesWidget()
        

    def widget_model(self):
        spacer_v = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return {
            "Осциллограф": {
                "Меню запуска": self.run_widget,
                "Измерение": self.measure_widget,
            }
        }



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