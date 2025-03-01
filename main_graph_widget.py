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

graph_widget_path = Path(__file__).parent
# Добавляем папку src в sys.path
sys.path.append(str(graph_widget_path))

######### Для встраивания в KPA #############
try:
    from kpa_async_pyqt_client.internal_bus.graph_widget.modbus_worker import ModbusWorker
    from kpa_async_pyqt_client.internal_bus.graph_widget.log_config import log_init
    from kpa_async_pyqt_client.internal_bus.graph_widget.tabWidget_maker import init_graph_window, create_tab_widget_items
    from kpa_async_pyqt_client.internal_bus.graph_widget.graph_widget import GraphWidget
    from kpa_async_pyqt_client.internal_bus.graph_widget.run_meas_widget import RunMaesWidget
except ImportError:
######### Для отдельного запуска через __main__ #############
    # from modbus_worker import ModbusWorker
    # from ddii_command import ModbusCMCommand, ModbusMPPCommand
    # from log_config import log_init
    from tabWidget_maker import init_graph_window, create_tab_widget_items
    from graph_widget import GraphWidget
    from run_meas_widget import RunMaesWidget


class MainGraphWidget(QtWidgets.QDialog):
    # lineEdit_T_cher                     : QtWidgets.QLineEdit
    # lineEdit_T_sipm                     : QtWidgets.QLineEdit
    # pushButton_OK                       : QtWidgets.QPushButton
    # vLayout_ser_connect                 : QtWidgets.QVBoxLayout
    # verticalLayout_graph                : QtWidgets.QVBoxLayout
    # verticalLayout_run_measure          : QtWidgets.QVBoxLayout
    mainGridLayout                      : QtWidgets.QGridLayout

    coroutine_get_temp_finished = QtCore.pyqtSignal()

    CM_DBG_SET_CFG = 0x0005
    CM_ID = 1
    #CM_DBG_SET_VOLTAGE = 0x0006
    #CM_DBG_GET_VOLTAGE = 0x0009
    #CMD_HVIP_ON_OFF = 0x000B

    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('DialogGraphWidget2.ui'), self)
        if __name__ == "__main__":
            pass
        else:
            pass
        # self.client = args[0]
            # self.cm_cmd: ModbusCMCommand = ModbusCMCommand(self.client, self.logger)
            # self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.client, self.logger)
        run_widget: RunMaesWidget =  RunMaesWidget()
        # self.mw = ModbusWorker()
        # self.logger = log_init()
        graph_widget: GraphWidget = GraphWidget()
        osc_widgets =  {"Измерение": run_widget}
        widget_model: Dict[str, Dict[str, QWidget]] = {"Осциллограмма": osc_widgets}
        init_graph_window(self.mainGridLayout, graph_widget, widget_model)
        self.flg_get_rst = 0

        self.task = None # type: ignore
        # self.pushButton_OK.clicked.connect(self.pushButton_OK_handler)
        # self.coroutine_get_temp_finished.connect(self.creator_task)
        # # инициализация структур обновляемых полей приложения
        # self.le_obj: list[LineEObj] = self.init_linEdit_list()


    # @asyncSlot()
    # async def get_client(self) -> None:
    #     """Перехватывает client от SerialConnect и переподключается к нему"""
    #     if self.w_ser_dialog.pushButton_connect_flag == 1:
    #         self.client: AsyncModbusSerialClient = self.w_ser_dialog.client
    #         await self.client.connect()
    #         self.cm_cmd = ModbusCMCommand(self.client, self.logger)
    #     if self.w_ser_dialog.pushButton_connect_flag == 0:
    #         if self.task:
    #             self.task.cancel()

    #     if self.w_ser_dialog.status_CM == 1:
    #         self.coroutine_get_temp_finished.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)
    # light(app)

    w: MainGraphWidget = MainGraphWidget()
    graph_widget: GraphWidget = GraphWidget()
    run_widget: RunMaesWidget =  RunMaesWidget()
    # osc_widgets =  {"Измерение": run_widget}
    # widget_model: Dict[str, Dict[str, QWidget]] = {"Осциллограмма": osc_widgets}
    # init_graph_window(w.mainGridLayout, graph_widget, widget_model)
    # spacer_g = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    # spacer_v = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    # grBox : QGroupBox = QGroupBox("Измерение")
    # # Настройка шрифта для QGroupBox
    # font = QFont()
    # font.setFamily("Arial")         # Шрифт
    # font.setPointSize(12)           # Размер шрифта
    # font.setBold(False)             # Жирный текст
    # font.setItalic(False)           # Курсив
    # grBox.setFont(font)
    # gridL: QGridLayout = QGridLayout()
    # # run_meas_widget = RunMaesWidget(client, logger)
    # w.verticalLayout_run_measure.addWidget(grBox)
    # grBox.setMinimumWidth(10)
    # grBox.setLayout(gridL)
    # gridL.addItem(spacer_g, 0, 0)
    # gridL.addItem(spacer_g, 0, 2)
    # gridL.addItem(spacer_v, 2, 1, 1, 3)
    # w.verticalLayout_graph.addWidget(graph_widget)
    # gridL.addWidget(run_widget)
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