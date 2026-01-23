import pyqtgraph as pg
from PyQt6 import QtWidgets
from qasync import asyncSlot
from pathlib import Path

import numpy as np
from typing import Optional, Sequence, Callable, Union


class GraphPen():
    '''Отрисовщик графиков

    Добавляет в layout окно графика и отрисовывет график
    '''
    def __init__(self,
                    layout: QtWidgets.QHBoxLayout | QtWidgets.QVBoxLayout | QtWidgets.QGridLayout,
                    name: str = "default_graph",
                    color: tuple = (255, 120, 10)) -> None:
        self.plt_widget = pg.PlotWidget()
        layout.addWidget(self.plt_widget)
        self.pen = pg.mkPen(color)
        self.name_frame: str = name
        #### Path ####
        # self.parent_path: Path = Path("./log/graph_data").resolve()
        # current_datetime = datetime.datetime.now()
        # time: str = current_datetime.strftime("%d-%m-%Y_%H-%M-%S-%f")[:23]
        # self.path_to_save: Path = self.parent_path / time

    @asyncSlot()
    async def draw_graph(self, data: list, name_file_save_data: Optional[str] = None, name_data: Optional[str] = None, path_to_save: Optional[Path] = None, save_log=False, clear=False) -> tuple[list, list]:
        if save_log and path_to_save:
            self.path_to_save: Path = path_to_save
        try:
            if any(isinstance(item, float) for item in data):
                data = list(map(int, data))
                # print(f"Данные преобразованы в int")
            x, y = await self._prepare_graph_data(data)
            if clear:
                self.plt_widget.clear()
                self.plot_item = None
            if save_log:
                # self._save_graph_data(x, y, name_file_save_data, name_data)
                pass
            if self.plot_item == None:
                self.plot_item = pg.PlotDataItem(x, y, pen = self.pen)
                self.plt_widget.addItem(self.plot_item)
            else:
                self.plot_item.setData(self.plot_item)
            # self.plt_widget.plot(x, y, pen=self.pen)
            return x, y
        except Exception as e:
            print(f"Ошибка отрисовки: {e}")
            return [],[]
    
    async def _prepare_graph_data(self, data):
        """Подготовка данных для графика"""
        x, y = [], []
        for index, value in enumerate(data):
            x.append(index)
            y.append(0 if value&0xFFF > 4000 else value&0xFFF)
            # self.delete_big_bytes(value)
            # y.append(value)
        return x, y

class HistPen():
    '''Отрисовщик гистограмм
    Добавляет в layout окно графика и отрисовывет гистограмму
    '''
    def __init__(self,
                layaut: QtWidgets.QHBoxLayout|QtWidgets.QVBoxLayout|QtWidgets.QGridLayout,
                name: str,
                color: tuple = (0, 0, 255, 150)) -> None:
        self.hist_widget: pg.PlotWidget  = pg.PlotWidget()
        layaut.addWidget(self.hist_widget)
        self.color = color
        self.pen = pg.mkPen(color)
        self.name_frame_data: str = name
        #### Path ####
        # self.parent_path: Path = Path("./log/hist_data").resolve()
        # current_datetime = datetime.datetime.now()
        # time: str = current_datetime.strftime("%d-%m-%Y_%H-%M-%S-%f")[:23]
        # self.path_to_save: str = str(self.parent_path / time)

    def draw_graph(self, data: list[int | float]) -> None:
        bin_count = 4096
        self.hist_widget.clear()
        y, x  = np.histogram(data, bins=np.linspace(0, bin_count, bin_count))
        self.hist_widget.plot(x, y, stepMode=True, fillLevel=0, brush=self.color)

    @asyncSlot()
    async def draw_hist(self, max_val: int | float) -> None:
        pass


