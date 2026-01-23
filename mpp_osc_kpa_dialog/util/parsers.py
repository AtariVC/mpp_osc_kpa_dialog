"""Различные парсеры
Парсер данных мпп
Парсер log
"""
import struct


class Parsers():
    def __init__(self, **kwargs):
        super().__init__()
    
    async def mpp_pars_16b(self, data: bytes) -> list[int]:
        """
        Преобразует кванты АЦП в int
        """
        data_out = [int.from_bytes(data[i:i+2], byteorder='big') for i in range(0, len(data), 2)]
        return data_out
    

    async def mpp_pars_32b(self, data: bytes) -> list[int]:
        """
        Преобразует кванты АЦП в int
        """
        data_out = [int.from_bytes(data[i:i+4], byteorder='big') for i in range(0, len(data), 4)]
        return data_out