from PyQt6 import QtWidgets, QtCore
from qtpy.uic import loadUi
from qasync import asyncSlot
import asyncio
import qtmodern.styles
import sys
import qasync
# from save_config import ConfigSaver
from pathlib import Path
from dataclasses import dataclass

try:
    from mpp_osc_kpa_dialog.util.plot_renderer import GraphPen
except:
    from util.plot_renderer import GraphPen


class GraphWidget(QtWidgets.QWidget):
    vLayout_pips                : QtWidgets.QVBoxLayout
    vLayout_sipm                : QtWidgets.QVBoxLayout

    vLayout_ser_connect         : QtWidgets.QVBoxLayout

    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('graph_widget.ui'), self)
        self.task = None # type: ignore

        self.gp_ch0 = GraphPen(self.vLayout_pips, name = "ch0", color = (255, 255, 0))
        self.gp_ch1 = GraphPen(self.vLayout_sipm, name = "ch1", color = (0, 255, 255))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qtmodern.styles.dark(app)
    w: GraphWidget = GraphWidget()
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    w.show()
    data: list = [1.4, 34.34, 324.4, 32.4, 89.4, 233.4, 234.4, 2344.4, 234.4]
    w.gp_pips.draw_graph(data, "test", clear=False) # type: ignore
    data1: list[int] = [1, 34, 45, 435, 234, 234, 2344 ,234, 23423, 324, 324234]
    w.gp_pips.draw_graph(data1, "test", clear=False) # type: ignore

    with event_loop:
        try:
            event_loop.run_until_complete(app_close_event.wait())
        except asyncio.CancelledError:
            ...