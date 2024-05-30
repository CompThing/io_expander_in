"""
Command line interface to IOE pin debouncing class

Show any changes in states of IOE input pins on command line output.
Outputs state of all 14 input pins as a single HEX value.
"""
from time import sleep

from io_expander_in import IoExpanderIn

I2C_BUS = 1


def example_callback(pin_num, state):
    """Simple callback for test purposes"""
    print(f"Pin {pin_num} changed: {state}")


def main():
    ioe_in = IoExpanderIn()
    for pin_num in range(1, 15):
        ioe_in.add_callback(pin_num, example_callback)
    while True:
        _changes = ioe_in.poll()
        sleep(0.1)


if __name__ == "__main__":
    main()
