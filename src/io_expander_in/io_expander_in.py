from typing import Tuple

import ioexpander
from ioexpander import ioe_regs

DEBOUNCE_LENGTH = 3
INIT_STATE = 0x1FFFF

PORT_REGISTERS = [
    ioe_regs.REGS.REG_P0,
    ioe_regs.REGS.REG_P1,
    ioe_regs.REGS.REG_P3,
]

# Map from register bits to external pin numbers
#  #	Port	ADC	PWM	Encoder
# 1	P1.5		[Ch 5]	Ch 1
# 2	P1.0		[Ch 2]	Ch 2
# 3	P1.2		[Ch 0]	Ch 3
# 4	P1.4		[Ch 1]	Ch 4
# 5	P0.0		[Ch 3]	Ch 5
# 6	P0.1		[Ch 4]	Ch 6
# 7	P1.1	[Ch 7]	Ch 1	Ch 7
# 8	P0.3	[Ch 6]	Ch 5	Ch 8
# 9	P0.4	[Ch 5]	Ch 3	Ch 9
# 10	P3.0	[Ch 1]		Ch 10
# 11	P0.6	[Ch 3]		Ch 11
# 12	P0.5	[Ch 4]	Ch 2	Ch 12
# 13	P0.7	[Ch 2]		Ch 13
# 14	P1.7	[Ch 0]		Ch 14

PIN_NUMBERS = {
    # Port: pin	ADC	PWM	Encoder
    8 + 5: 1,
    8 + 0: 2,
    8 + 2: 3,
    8 + 4: 4,
    0 + 0: 5,
    0 + 1: 6,
    8 + 1: 7,
    0 + 3: 8,
    0 + 4: 9,
    16 + 0: 10,
    0 + 6: 11,
    0 + 5: 12,
    0 + 7: 13,
    8 + 7: 14
}


class IoExpanderIn:
    """
    3 * 8-bit ports combined into single 24-bit number 
    """
    def __init__(self, smbus_id=1, i2c_addr=0x18):
        self.io_expander = ioexpander.IOE(    # pylint: disable=unexpected-keyword-arg
            i2c_addr=i2c_addr,
            smbus_id=smbus_id
        )
        for input_pin in range(1, 15):
            self.io_expander.set_mode(input_pin, ioexpander.IN_PU)
        self.ports = INIT_STATE
        self.port_samples = [INIT_STATE] * DEBOUNCE_LENGTH
        self.callbacks = {}

    def poll(self):
        """
        Poll and debouce 3 IO pin registers

        If registers have changed call appropriate callbacks
        """
        new_ports = 0
        for port_num in range(3):
            new_ports += self.io_expander.i2c_read8(PORT_REGISTERS[port_num]) << 8 * port_num
        self.port_samples.pop()
        self.port_samples.insert(0, new_ports)
        stable_ones = self.port_samples[0] 
        stable_zeroes = self.port_samples[0]
        for sample_num in range(1, DEBOUNCE_LENGTH):
            stable_ones = stable_ones & self.port_samples[sample_num]
            stable_zeroes = stable_zeroes | self.port_samples[sample_num]
        # Set stable ones
        new_ports = new_ports | stable_ones
        # Clear stable zeroes
        new_ports = new_ports & stable_zeroes
        changes = new_ports ^ self.ports
        self.ports = new_ports
        self.process_callbacks(changes)
        return changes

    def add_callback(self, pin_num: int, callback: callable):
        self.callbacks[pin_num] = callback

    def process_callbacks(self, changes):
        """
        Call any callbacks for changed pins
        """
        for bit_num in range(18):
            changed = bool((changes >> bit_num) & 0x01)
            if changed:
                pin_num = PIN_NUMBERS.get(bit_num, None)
                pin_state = (self.ports >> bit_num) & 0x01
                if pin_num is not None:
                    callback = self.callbacks.get(pin_num, None)
                    if callback:
                        callback(pin_num, pin_state)
