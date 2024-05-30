# IO Expander In

## Summary
Use a Pimoroni IO Expander entirely for a set of input Buttons

## Why
Using an IO Expander for debounced input buttons using standard Pimoroni package
and a button debouncing package requires consderable I2C overhead, with an I2C
read required for each pin that is read. Additionally debouncing 14 pins separately
requires the debounce to be repeated for each pin.
The 14 IO pins of a Pimoroni IO expander are spread across 3 registers. Reading all
14 pins can therefore be redcuced from 14 down to 3 I2C reads.
Combining the 3 * 8 bit registers into a single integer allows debounced changes to
be detected using simple bit-wise logic on 3 copies of the single integer, giving
a 14 times improvement in core change detection logic.

## Using the package
An instance of the IO Exapnder In class can be created for all input pins.
A callback then needs to be registered for each input pin in use.
A poll method of the IO Expander is called at regular intervals, typicallu 0.1s
If the poll method detects debounced button changes, it calls the registered
callback with the pin number and new pin state as arguments.
