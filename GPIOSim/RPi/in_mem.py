#!/usr/bin/python
# -*- coding: utf-8 -*-
"""In memory GPIO simulator """

import time

from GPIOSim.RPi.common import *  # pylint: disable=W0614,W0401,W0622


DATA = {}


def init():  # pylint: disable=E0102
    """Init GPIO"""
    # Set default values
    for i in range(0, 40):
        if "pin" + str(i) not in DATA:
            DATA['pin' + str(i)] = {}

        DATA["pin" + str(i)]["state"] = str(GPIO_STATE_DEFAULT[i])
        DATA["pin" + str(i)]["value"] = "0"


def set_pin_value(pin, value):  # pylint: disable=E0102
    """Set arbitrary value to a pin

    This is useful to simulate a state change of pin
    """
    DATA[pin]["value"] = value


def setup(pin, mode, initial=LOW, pull_up_down=PUD_OFF):  # pylint: disable=W0613,E0102
    """Set the input or output mode for a specified pin. Mode should be
    either OUT or IN."""
    pin = GPIO_NAMES.index("GPIO" + str(pin))

    if int(DATA["pin" + str(pin)]["state"]) == 0:
        raise Exception

    DATA["pin" + str(pin)]["state"] = str(mode)
    if mode == OUT:
        DATA["pin" + str(mode)]["value"] = initial


def output(pin, value):  # pylint: disable=E0102
    """Set the specified pin the provided high/low value. Value should be
    either HIGH/LOW or a boolean (true = high)."""

    pin = GPIO_NAMES.index("GPIO" + str(pin))
    if int(DATA["pin" + str(pin)]["state"]) != OUT:
        raise Exception

    DATA["pin" + str(pin)]["value"] = str(value)


def input(pin):  # pylint: disable=E0102,W0622
    """Read the specified pin and return HIGH/true if the pin is pulled high,
    or LOW/false if pulled low."""
    pin = GPIO_NAMES.index("GPIO" + str(pin))

    return int(DATA["pin" + str(pin)]["value"])


class Eventer(CommonEventer):
    """Detect pin state changes"""

    def __init__(self):
        CommonEventer.__init__(self)

    def stop(self):
        """Stop Eventer"""
        self.running = False

    def run(self):
        """Start Eventer"""
        while self.running:
            for key, section in DATA.items():
                # TODO find what means state
                if self.old_conf.get(key, {}).get('value') is not None and \
                        int(section['state']) == 1:
                    # RISING and BOTH
                    if self.old_conf[key]['value'] == 0 and int(section['value']) == 1:
                        if EVENT_DETECTOR[PIN_TO_GPIO[key]] \
                                in [RISING, BOTH]:
                            callback = Callbacker(PIN_TO_GPIO[key])
                            callback.start()
                    # FALLING and BOTH
                    elif self.old_conf[key]['value'] == 1 and int(section['value']) == 0:
                        if EVENT_DETECTOR[PIN_TO_GPIO[key]] \
                                in [FALLING, BOTH]:
                            callback = Callbacker(PIN_TO_GPIO[key])
                            callback.start()
                # save values
                if self.old_conf.get(key) is None:
                    self.old_conf[key] = {}
                self.old_conf[key]['value'] = int(section['value'])
                self.old_conf[key]['state'] = int(section['state'])
            # Sleep
            time.sleep(0.01)
