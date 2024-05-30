"""
digitalio compatibility layer for Pimoroni Digital IO.

Pimoroni has its own I2C API for connection to its IO
expander.
This module presents that in a way that matches native GPIO
or other IO expanders.
"""
from dataclasses import dataclass

import ioexpander


@dataclass(frozen=True, init=False)
class Direction:
    INPUT = ioexpander.IN_PU
    OUTPUT = ioexpander.PIN_MODE_PP


class DigitalInOut:  # pylint: disable = too-few-public-methods
    """
    Make Pimoroni IO Expander GPIO look like native GPIO.

    Present an API that looks similar to DigitalInOut of
    real digitalio library or Adafruit Seesaw digitalio
    """

    _io_expander = None

    def __init__(self, pin, smbus_id=1, i2c_addr=0x18):
        self.pin = pin
        if self.__class__._io_expander is None:
            self.io_expander = ioexpander.IOE(    # pylint: disable=unexpected-keyword-arg
                i2c_addr=i2c_addr,
                smbus_id=smbus_id
            )
        self.io_expander.set_mode(pin, ioexpander.IN_PU)

    @property
    def value(self):
        return self.io_expander.input(self.pin)
