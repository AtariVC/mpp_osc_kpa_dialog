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
from kpa_config.config import ModulesNames
from kpa_async_pyqt_client.Base_Module_Backend import Module_Backend
from kpa_async_driver.modules.internal_bus_driver import Internal_Bus_Driver
from kpa_async_pyqt_client.impact.backend import Impact_Backend

graph_widget_path = Path(__file__).parent
# Добавляем папку src в sys.path
sys.path.append(str(graph_widget_path))

######### Для встраивания в KPA #############
try:
    from mpp_osc_kpa_dialog.util.main_window_maker import create_split_widget, create_tab_widget_items
    from mpp_osc_kpa_dialog.modules.graph_widget import GraphWidget
    from mpp_osc_kpa_dialog.modules.run_meas_widget import RunMaesWidget
    from mpp_osc_kpa_dialog.modules.measure_widget import MeasureWidget
except:
    from util.main_window_maker import create_split_widget, create_tab_widget_items
    from modules.graph_widget import GraphWidget
    from modules.run_meas_widget import RunMaesWidget
    from modules.measure_widget import MeasureWidget

# verticalLayout_3

class MPP_Osc_Dialog(Module_Backend):
    mainGridLayout : QtWidgets.QGridLayout

    coroutine_get_temp_finished = QtCore.pyqtSignal()

    def __init__(self, parent, **kwargs) -> None:
        self.module_driver: Internal_Bus_Driver = Internal_Bus_Driver(**kwargs)
        super().__init__(self.module_driver.label,
                         path=Path(__file__).parent.joinpath('main.ui'),
                         **kwargs)
        # loadUi(Path(__file__).parent.joinpath('main.ui'), self)
        # add button on kpa_async_pyqt_client.impact
        # try:
        #     self.parent = parent
        #     self.impact_module: Impact_Backend = parent.impact_module # type.ignore
        #     self.pushButton_osc: QtWidgets.QPushButton = QtWidgets.QPushButton()
        #     self.pushButton_osc.setText('Осциллограммы')
        #     self.impact_module.verticalLayout_3.addWidget(self.pushButton_osc)
        #     self.pushButton_osc.clicked.connect(self.pushButton_osc_handler)
        # except Exception as e:
        #     logger.error(e)
        self.init_widgets()


    def init_widgets(self) -> None:
        # Виджеты
        self.w_graph_widget: GraphWidget = GraphWidget()
        self.measure_widget: MeasureWidget = MeasureWidget()
        self.run_widget: RunMaesWidget =  RunMaesWidget(self)
        model = self.widget_model()
        self.tab_widget = create_tab_widget_items(model)
        create_split_widget(self.mainGridLayout, self.w_graph_widget, self.tab_widget)
        

    def widget_model(self):
        return {
            "Осциллограф": {
                "Меню запуска": self.run_widget,
                "Измерение": self.measure_widget,
            }
        }
    


# async def connect(module: MPP_Osc_Dialog):
#     await module.connect_module()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    qtmodern.styles.dark(app)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    parent = None
    module: MPP_Osc_Dialog = MPP_Osc_Dialog(parent, show_connection_status=True)
    # asyncio.run(connect)
    module.show()

    with event_loop:
        try:
            event_loop.run_until_complete(app_close_event.wait())
        except asyncio.CancelledError:
            ...