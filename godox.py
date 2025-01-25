import asyncio
from bleak import BleakClient, BleakScanner
from crccheck.crc import Crc8Maxim
import logging

WRITE_UUID_1 = "dad0215c-9754-4264-9174-4736e23ef493"
WRITE_UUID_2 = "1c466d7c-6b01-4943-9e9f-cd65b6d2b675"
LOGGER = logging.getLogger(__name__)

async def discover():
    """Bluetooth LE cihazlarını keşfedin."""
    devices = await BleakScanner.discover()
    LOGGER.debug("Keşfedilen cihazlar: %s", [{"address": device.address, "name": device.name} for device in devices])
    return [device for device in devices if device.name.startswith("GD_LED")]

class GodoxInstance:
    def __init__(self, mac: str, uuid: str) -> None:
        self._mac = mac
        self._uuid = uuid
        self._device = BleakClient(self._mac)
        self._is_on = None
        self._connected = None
        self._brightness = None

    async def _send(self, data: bytearray):
        LOGGER.debug(''.join(format(x, '03x') for x in data))
        
        if not self._connected:
            await self.connect()

        crcinst = Crc8Maxim()
        crcinst.process(data)
        await self._device.write_gatt_char(self._uuid, data + crcinst.finalbytes())

    @property
    def mac(self):
        return self._mac

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    async def set_brightness(self, intensity: int):
        header = bytes.fromhex("f0d10501")
        command = bytes([intensity])
        params = bytes.fromhex("380c01")

        await self._send(header + command + params)
        self._brightness = intensity

    async def turn_on(self):
        header = bytes.fromhex("f0d0060c")
        command = bytes.fromhex("01")
        params = bytes.fromhex("00000000")

        await self._send(header + command + params)
        self._is_on = True

    async def turn_off(self):
        header = bytes.fromhex("f0d0060c")
        command = bytes.fromhex("00")
        params = bytes.fromhex("00000000")

        await self._send(header + command + params)
        self._is_on = False

    async def connect(self):
        await self._device.connect(timeout=20)
        await asyncio.sleep(1)
        self._connected = True

    async def disconnect(self):
        if self._device.is_connected:
            await self._device.disconnect()

async def main():
    device_1 = GodoxInstance("A4:C1:38:00:B6:0D", WRITE_UUID_1)
    device_2 = GodoxInstance("A4:C1:38:2C:CB:00", WRITE_UUID_2)

    # Cihazları aç
    await device_1.turn_on()
    await device_2.turn_on()

    await device_1.set_brightness(255)
    await device_2.set_brightness(128)

    # Bağlantıları kes
    await device_1.disconnect()
    await device_2.disconnect()

asyncio.run(main())
