from typing import Literal
from kpa_async_driver.modbus_stream.stream_decoder import ModbusStreamDecoder
from kpa_async_driver.modbus_stream.packet_types import ModbusFrame
from loguru import logger
import struct
import asyncio

try:
    from mpp_osc_kpa_dialog.util.env_var import EnvironmentVar
except:
    from util.env_var import EnvironmentVar

class ModbusMPPCommand(EnvironmentVar):
    def __init__(self, modbus: ModbusStreamDecoder, id: int):
        super().__init__()
        self.id = id
        self.modbus: ModbusStreamDecoder = modbus

    @staticmethod
    def complete_cmd(ch:int, cmd_reg:int, param:int|list|None = None):
        cmd = (0,)
        if isinstance(param, int): 
            cmd = (((ch & 0xFF)<<8 )|(cmd_reg & 0xFF), param)
        if isinstance(param, list): 
            cmd = tuple([((ch & 0xFF)<<8 )|(cmd_reg & 0xFF)] + param)
        if param is None: 
            cmd = (((ch & 0xFF)<<8 )|(cmd_reg & 0xFF),)
        return struct.pack('>'+'H'*len(cmd), *cmd)

    async def read_oscill(self, ch: int = 0) -> bytes:
        # TODO: убрать эхо
        try:
            all_data = bytearray()
            for offset in range(0, 512, 64):
                reg_addr = (self.MPP_REG_OSCILL_CH1 if ch == 1 else self.MPP_REG_OSCILL_CH0) + offset
                answer: ModbusFrame | None = await self.modbus.read_modbus(self.id, 3, 64, reg_addr)
                # await asyncio.sleep(0.1)
                if answer:
                    all_data.extend(answer._raw_data[3:-2])
                else:
                    logger.error(f'Mpdule with id={self.id} don\'t answer')
            return bytes(all_data)
        except Exception as e:
            logger.error(e)
            return b'-1'
    
    async def set_level(self, ch:Literal[0,1], lvl:int) -> None:
        data = self.complete_cmd(ch, self.MPP_SET_LEVEL, lvl)
        try:
            answer: ModbusFrame | None = await self.modbus.write_modbus(self.id, 16, self.MPP_CTRL, data)
            if answer:
                pass
            else:
                logger.error(f'Mpdule with id={self.id} don\'t answer')
        except Exception as e:
            logger.error(e)
            
    async def start_measure(self, ch:Literal[0,1], state:int) -> None:
        data = self.complete_cmd(ch, self.MPP_START_MEASURE, state)
        try:
            answer: ModbusFrame | None = await self.modbus.write_modbus(self.id, 16, 0, data)
            if answer:
                pass
            else:
                logger.error(f'Mpdule with id={self.id} don\'t answer')
        except Exception as e:
            logger.error(e)
            
    async def start_forced(self, ch:Literal[0, 1]) -> None:
        data = self.complete_cmd(ch, self.MPP_FORCED_START)
        try:
            answer: ModbusFrame | None = await self.modbus.write_modbus(self.id, 16, 0, data)
            if answer:
                pass
            else:
                logger.error(f'Mpdule with id={self.id} don\'t answer')
        except Exception as e:
            logger.error(e)


        