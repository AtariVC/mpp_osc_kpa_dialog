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


class RunMaesWidget(QtWidgets.QDialog):
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

    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('run_meas_widget_bdk2.ui'), self) 
        self.parent = args[0]
        self.logger = logger
        # self.mw = ModbusWorker()
        # self.parser = Parsers()
        try:
            self.lineEdit_ID : QtWidgets.QLineEdit # for run_meas_widget_comm.ui
            self.id = int(self.lineEdit_ID.text())
        except Exception:
            self.comboBox_module_mpp : QtWidgets.QComboBox  # for run_meas_widget_bdk2.ui
            modules_mpp = {'МПП-1': 4, 'МПП-2': 5, 'МПП-3': 6, 'МПП-4': 7,'МПП-5': 8, 'МПП-6': 9, 'МПП-7': 3}
            self.comboBox_module_mpp.addItems(modules_mpp.keys())
        # self.client = args[0]
        # if __name__ != "__main__":
            # self.client = args[0]
            # self.logger = args[1]
            # self.cm_cmd: ModbusCMCommand = ModbusCMCommand(self.client, self.logger)
            # self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.client, self.logger)
        #     pass
        # try:
            # self.client = args[0]
            # self.modbus_stream: ModbusStreamDecoder = ModbusStreamDecoder()
            # self.client.module_driver.uart1.received.subscribe(self.get_mpp_osc_data)
        # except:
        #     pass
        # self.pushButton_autorun.clicked.connect(self.pushButton_autorun_handler)
        # self.gp_ch1 = GraphPen(self.grph_wdgt.vLayout_pips, name = "ch1", color = (255, 255, 0))
        # self.gp_ch2 = GraphPen(self.grph_wdgt.vLayout_sipm, name = "ch2", color = (0, 255, 255))
        # self.ch1_data: list[int] = []
        # self.ch2_data: list[int] = []
        self.run_mes_flag = 0
        self.pushButton_run.clicked.connect(self.pushButton_run_handler)


        # self.checkBox_enable_test_csa.clicked.connect(self.checkBox_enable_test_csa_handler)

    # def pushButton_autorun_handler(self) -> None:
    #     self.pushButton_autorun_signal.emit()

    def pushButton_run_handler(self) -> None:
        # self.pushButton_run_trig_pips_signal.emit()
        # self.
        pass


    @qasync.asyncSlot()
    async def pushButton_forced_meas_handler(self):
        if self.run_mes_flag == 0:
            self.run_mes_flag = 1
            self.pushButton_run_source_text: str = self.pushButton_run.text()
            self.pushButton_run.setText("Остановить")
            # self.pushButton_run.setEnabled(False)
            try:
                await self.cmd_mpp_read_osc()
            except Exception as e:
                print(e)
        else:
            self.pushButton_run.setText(self.pushButton_run_source_text)
            self.client.module_driver.uart1.received.unsubscribe(self.get_mpp_osc_data)
            self.forced_meas_process_flag = 0
        # TODO: создать задачу измерения 

    @qasync.asyncSlot()
    async def get_mpp_osc_data(self, data: bytes):
        frames: list[ModbusFrame] = self.modbus_stream.get_modbus_packets(data)
        try:
            if len(frames) > 0:
                for frame in frames:
                    if frame.device_id == self.id and hasattr(frame, 'data'):
                        if isinstance(frame.data, bytes):
                            # print(len(frame.data))
                            # print(frame.data.hex(" ").upper())
                            for i in range((AMNT_RD_RG-1)):
                                self.ch1_data.append(int(struct.unpack('<H', frame.data[i*2:(i+1)*2])[0]))
                            print(self.ch1_data)
                            print(len(self.ch1_data))
                            if len(self.ch1_data) >= 512:
                                await self.gp_ch1.draw_graph(self.ch1_data, "ch1", clear=False)
                                self.ch1_data.clear()
                                self.ch2_data.clear()
                            
        except TypeError as err:
            logger.exception(err)

    @qasync.asyncSlot()
    async def cmd_mpp_read_osc(self):
        first_reg = 0xA000
        read_amount = AMNT_RD_RG
        self.id = int(self.lineEdit_ID.text())
        if 2 < self.id < 7:
            addr: int = self.id
        else:
            logger.warning(f"addr = {self.id} is not [2..7] or not num")
        cmd_code = 0x03
        await self.mpp_forced_launch(addr, 0)
        while self.forced_meas_process_flag == 1:
            try:
                tx_data = self.client._gen_modbus_packet(addr, cmd_code, read_amount, first_reg, b'')
                await self.client.uart.send(data_bytes=tx_data)
                await asyncio.sleep(0.01)
                if first_reg <= 0xA1FF:
                    first_reg += AMNT_RD_RG
                else:
                    first_reg = 0xA000
                    await self.mpp_forced_launch(addr, 0)
                    self.forced_meas_process_flag = 0
            except Exception as err:
                logger.warning(err)
                break

    @qasync.asyncSlot()
    async def mpp_forced_launch(self, addr:int, ch: int):
        tx: int = 0x51 | (ch<<8)
        tx_b = tx.to_bytes(2, "big")
        tx_data: bytes = self.client._gen_modbus_packet(addr, 0x06, 0, 0x0001, tx_b)
        # print (bytes.hex(" ").upper())
        await self.client.uart.send(data_bytes=tx_data)





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



