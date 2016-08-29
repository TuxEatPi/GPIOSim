#!/usr/bin/python
# -*- coding: utf-8 -*-
"""In memory GPIO simulator """

from configparser import RawConfigParser
import os
import tempfile
from threading import Lock
import time


from GPIOSim.RPi.common import *  # pylint: disable=W0614,W0622,W0401


WORK_DIR = os.path.join(tempfile.gettempdir(), "GPIOSim")
WORK_FILE = os.path.join(WORK_DIR, "pins.ini")
PARSER = RawConfigParser()
LOCK = Lock()


def _read():
    """Read data from disk"""
    PARSER.read(WORK_FILE)


def _write():
    """Write data on disk"""
    LOCK.acquire()
    with open(WORK_FILE, 'w') as configfile:
        PARSER.write(configfile)
    LOCK.release()


def init():  # pylint: disable=E0102
    """Init GPIO"""
    # create folder
    if not os.path.exists(WORK_DIR):
        os.makedirs(WORK_DIR)

    _read()
    # Set default values
    for i in range(0, 40):
        if not PARSER.has_section("pin" + str(i)):
            PARSER.add_section("pin" + str(i))

        PARSER.set("pin" + str(i), "state", str(GPIO_STATE_DEFAULT[i]))
        PARSER.set("pin" + str(i), "value", "0")

    _write()


def set_pin_value(pin, value):  # pylint: disable=E0102
    """Set arbitrary value to a pin

    This is useful to simulate a state change of pin
    """
    _read()
    PARSER.set(pin, "value", value)
    _write()


def setup(pin, mode, initial=LOW, pull_up_down=PUD_OFF):  # pylint: disable=W0613,E0102
    """Set the input or output mode for a specified pin. Mode should be
    either OUT or IN."""
    _read()

    pin = GPIO_NAMES.index("GPIO" + str(pin))

    if PARSER.getint("pin" + str(pin), "state") == 0:
        raise Exception

    PARSER.set("pin" + str(pin), "state", str(mode))
    if mode == OUT:
        PARSER.set("pin" + str(mode), "value", "0")

    _write()


def output(pin, value):  # pylint: disable=E0102
    """Set the specified pin the provided high/low value. Value should be
    either HIGH/LOW or a boolean (true = high)."""
    _read()
    pin = GPIO_NAMES.index("GPIO" + str(pin))

    if PARSER.getint("pin" + str(pin), "state") != OUT:
        raise Exception

    PARSER.set("pin" + str(pin), "value", str(value))
    _write()


def input(pin):  # pylint: disable=E0102
    """Read the specified pin and return HIGH/true if the pin is pulled high,
    or LOW/false if pulled low."""
    pin = GPIO_NAMES.index("GPIO" + str(pin))

    _read()
    return PARSER.Getint("pin" + str(pin), "value")


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
            _read()
            for key, section in PARSER.items():
                # TODO find what means state
                if self.old_conf.get(key, {}).get('value') is not None \
                        and section.getint('state') == 1:
                    # RISING and BOTH
                    if self.old_conf[key]['value'] == 0 and section.getint('value') == 1:
                        if EVENT_DETECTOR[PIN_TO_GPIO[key]] in [RISING, BOTH]:
                            callback = Callbacker(PIN_TO_GPIO[key])
                            callback.start()
                    # FALLING and BOTH
                    if self.old_conf[key]['value'] == 1 and section.getint('value') == 0:
                        if EVENT_DETECTOR[PIN_TO_GPIO[key]] in [FALLING, BOTH]:
                            callback = Callbacker(PIN_TO_GPIO[key])
                            callback.start()
                # save values
                if self.old_conf.get(key) is None:
                    self.old_conf[key] = {}
                self.old_conf[key]['value'] = section.getint('value')
                self.old_conf[key]['state'] = section.getint('state')
            # Sleep
            time.sleep(0.01)
