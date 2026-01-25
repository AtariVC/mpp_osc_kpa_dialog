import pyqtgraph as pg
from PyQt6 import QtWidgets
from qasync import asyncSlot
from pathlib import Path
from loguru import logger
import qasync
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
        self.logger = logger
        self.plt_widget = pg.PlotWidget()
        layout.addWidget(self.plt_widget)
        self.pen = pg.mkPen(color)
        self.name_frame: str = name
        self.plot_item: pg.PlotDataItem # для PlotDataItem
        # Threshold for selective saving (None disables filtering)
        self._save_threshold: int | None = None
        # Window size for spike detection (neighbors on each side)
        self._spike_window: int = 1

    @qasync.asyncSlot()
    async def draw_graph(self, data: list, name_file_save_data: Optional[str] = None, name_data: Optional[str] = None, path_to_save: Optional[Path] = None, save_log=False, clear=True, filter: Optional[Callable] = None):
        try:
            if any(isinstance(item, float) for item in data):
                data = list(map(int, data))
                # print(f"Данные преобразованы в int")
            x, y = await self._prepare_graph_data(data)
            if clear: # очищать ли график. Если нет, то новые точки просто добавляются на график
                self.plt_widget.clear()
                self.plot_item = pg.PlotDataItem(x, y, pen = self.pen)
                self.plt_widget.addItem(self.plot_item)
            else:
                # обновляем существующие данные
                self.plot_item.setData(x, y)
            return x, y
        except Exception as e:
            self.logger.error(f"Ошибка отрисовки: {e}")
            return [],[]
    
    async def _prepare_graph_data(self, data):
        """Подготовка данных для графика"""
        x, y = [], []
        for index, value in enumerate(data):
            x.append(index)
            # y.append(0 if value&0xFFF > 4000 else value&0xFFF)
            y.append(value&0xFFF)
            # self.delete_big_bytes(value)
            # y.append(value)
        return x, y

