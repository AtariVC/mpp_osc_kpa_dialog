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
try:
    from kpa_parser.modbus_frame import crc16
    from kpa_parser.modbus_frame.packet_types import ModbusFrame
    from kpa_parser.modbus_frame.stream_decoder import ModbusStreamDecoder
except ImportError:
    pass
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
    pushButton_forced_meas       : QtWidgets.QPushButton
    checkBox_enable_test_csa     : QtWidgets.QCheckBox
    gridLayout_meas              : QtWidgets.QGridLayout
    lineEdit_ID                  : QtWidgets.QLineEdit

    # pushButton_autorun_signal           = QtCore.pyqtSignal()
    # pushButton_run_trig_pips_signal     = QtCore.pyqtSignal()
    # checkBox_enable_test_csa_signal     = QtCore.pyqtSignal()

    def __init__(self, *args) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('WidgetRunMeasure.ui'), self)
        # self.mw = ModbusWorker()
        # self.parser = Parsers()

        self.task = None
        self.forced_meas_process_flag = 0
        self.id = int(self.lineEdit_ID.text())
        self.pushButton_run.setEnabled(False)
        # self.client = args[0]
        if __name__ != "__main__":
            # self.client = args[0]
            # self.logger = args[1]
            # self.cm_cmd: ModbusCMCommand = ModbusCMCommand(self.client, self.logger)
            # self.mpp_cmd: ModbusMPPCommand = ModbusMPPCommand(self.client, self.logger)
            pass
        try:
            self.client = args[0]
            self.modbus_stream: ModbusStreamDecoder = ModbusStreamDecoder()
            self.client.module_driver.uart1.received.subscribe(self.get_mpp_osc_data)
        except:
            pass
        # self.pushButton_autorun.clicked.connect(self.pushButton_autorun_handler)
        self.pushButton_run.clicked.connect(self.pushButton_run_handler)
        self.pushButton_forced_meas.clicked.connect(self.pushButton_forced_meas_handler)

        # self.checkBox_enable_test_csa.clicked.connect(self.checkBox_enable_test_csa_handler)

    # def pushButton_autorun_handler(self) -> None:
    #     self.pushButton_autorun_signal.emit()

    def pushButton_run_handler(self) -> None:
        # self.pushButton_run_trig_pips_signal.emit()
        # self.
        pass

    # def checkBox_enable_test_csa_handler(self, state) -> None:
    #     print(state)

    @qasync.asyncSlot()
    async def pushButton_forced_meas_handler(self):
        if self.forced_meas_process_flag == 0:
            self.forced_meas_process_flag = 1
            self.pushButton_forced_meas.setText("Остановить")
            # self.pushButton_run.setEnabled(False)
            try:
                await self.cmd_mpp_read_osc()
            except Exception as e:
                print(e)

        else:
            self.pushButton_forced_meas.setText("Принуд. запуск")
            self.client.module_driver.uart1.received.unsubscribe(self.get_mpp_osc_data)
            self.forced_meas_process_flag = 0

    @qasync.asyncSlot()
    async def get_mpp_osc_data(self, data: bytes):
        frames: list[ModbusFrame] = self.modbus_stream.get_modbus_packets(data)
        if len(frames) > 0:
            for frame in frames:
                if frame.device_id == self.id and hasattr(frame, 'data'):
                    if len(frame.data) == AMNT_RD_RG*2:
                        print(frame.data.hex(" ").upper())

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
                if first_reg <= 0xA1FF:
                    first_reg += 64
                else:
                    first_reg = 0xA000
                    # await self.mpp_forced_launch(addr, 0)
                self.forced_meas_process_flag = 0
            except Exception as err:
                logger.warning(err)
                self.forced_meas_process_flag = 0
                break


    @qasync.asyncSlot()
    async def mpp_forced_launch(self, addr:int, ch: int):
        tx: int = 0x51 | (ch<<8)
        tx_b = tx.to_bytes(2, "big")
        tx_data: bytes = self.client._gen_modbus_packet(addr, 0x06, 0x0, 0x0001, tx_b)
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



