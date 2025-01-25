import logging
from homeassistant.components.light import LightEntity
from .godox import GodoxInstance

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the Godox light from a config entry."""
    mac_address = config_entry.data["mac_address"]
    device = GodoxInstance(mac_address)
    async_add_devices([GodoxLight(device)])

class GodoxLight(LightEntity):
    """Representation of a Godox Light."""

    def __init__(self, device: GodoxInstance):
        """Initialize the light."""
        self._device = device
        self._name = f"Godox {device.mac}"
        self._is_on = False
        self._brightness = 255

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return if the light is on."""
        return self._is_on

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    async def turn_on(self, **kwargs):
        """Turn the light on."""
        await self._device.turn_on()
        self._is_on = True
        _LOGGER.info(f"Turned on light: {self._name}")

    async def turn_off(self, **kwargs):
        """Turn the light off."""
        await self._device.turn_off()
        self._is_on = False
        _LOGGER.info(f"Turned off light: {self._name}")

    async def set_brightness(self, brightness: int):
        """Set the brightness of the light."""
        await self._device.set_brightness(brightness)
        self._brightness = brightness
        _LOGGER.info(f"Set brightness of light: {self._name} to {brightness}")
