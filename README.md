# button-poe

Expose a button to Home Assistant using a PoE FeatherWing.

For use with Adafruit Feather boards.

## Setup

Install these [CircuitPython libraries](https://circuitpython.org/libraries):

* adafruit_wiznet5k
* adafruit_debouncer
* adafruit_requests
* neopixel

Copy `config_sample.py` to `config.py` and fill it out to match your setup.

Wire a button to GND and D9, and add a [PoE FeatherWing](https://www.crowdsupply.com/silicognition/poe-featherwing).
