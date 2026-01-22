from kpa_async_driver.modbus_stream.stream_decoder import ModbusStreamDecoder
from kpa_async_driver.modbus_stream.packet_types import ModbusFrame
from loguru import logger

try:
    from mpp_osc_kpa_dialog.util.env_var import EnvironmentVar
except:
    from util.env_var import EnvironmentVar

class ModbusMPPCommand(EnvironmentVar):
    def __init__(self, modbus: ModbusStreamDecoder, id: int):
        super().__init__()
        self.id = id
        self.modbus: ModbusStreamDecoder = modbus


    async def read_oscill(self, ch: int = 0) -> bytes:
        try:
            all_data = bytearray()
            for offset in range(0, 512, 64):
                reg_addr = (self.REG_OSCILL_CH1 if ch == 1 else self.REG_OSCILL_CH0) + offset
                answer: ModbusFrame | None = await self.modbus.read_modbus(self.id, 3, 64, reg_addr)
                if answer:
                    all_data.extend(answer.data)
                else:
                    logger.error(f'Mpdule with id={self.id} don\'t answer')
            return bytes(all_data)
        except Exception as e:
            logger.error(e)
            return b'-1'
    
    async def set_level(self, ch: int[0, 1], lvl: int) -> None:
        data = [((ch & 0xFF)<<4 )|(self.REG_MPP_LEVEL & 0xFF), lvl]
        try:
            answer: ModbusFrame | None = await self.modbus.write_modbus(self.id, 0x12, 0, data)
            if answer:
                pass
            else:
                logger.error(f'Mpdule with id={self.id} don\'t answer')
        except Exception as e:
            logger.error(e)
            
    async def start_measure(self, ch: int[0, 1], state: int) -> None:
        data = [((ch & 0xFF)<<4 )|(self.MPP_START_MEASURE & 0xFF), state]
        try:
            answer: ModbusFrame | None = await self.modbus.write_modbus(self.id, 0x12, 0, data)
            if answer:
                pass
            else:
                logger.error(f'Mpdule with id={self.id} don\'t answer')
        except Exception as e:
            logger.error(e)
            
    async def start_forced(self, ch: int[0, 1], state: int) -> None:
        data = [((ch & 0xFF)<<4 )|(self.MPP_START_MEASURE_FORCED & 0xFF)]
        try:
            answer: ModbusFrame | None = await self.modbus.write_modbus(self.id, 0x12, 0, data)
            if answer:
                pass
            else:
                logger.error(f'Mpdule with id={self.id} don\'t answer')
        except Exception as e:
            logger.error(e)
        