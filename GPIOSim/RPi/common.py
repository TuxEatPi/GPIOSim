#!/usr/bin/python
# -*- coding: utf-8 -*-
"""In memory GPIO simulator """

from threading import Thread

# Set dict
EVENT_DETECTOR = {}
EVENT_CALLBACK = {}


OUT = 2
IN = 1  # pylint: disable=C0103
HIGH = 1
LOW = 0

RISING = 1
FALLING = 2
BOTH = 3

PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2

# TODO find true value

GPIO_STATE_DEFAULT = [0, 0,  # 3v3   , 5v
                      3, 0,  # GPIO2 , 5V
                      3, 0,  # GPIO3 , GND
                      3, 3,  # GPIO4 , GPIO14
                      0, 3,  # GND   , GPIO15
                      3, 3,  # GPIO17, GPIO18
                      3, 0,  # GPIO27, GND
                      3, 3,  # GPIO22, GPIO23
                      0, 3,  # 3V3   , GPIO24
                      3, 0,  # GPIO10, GND
                      3, 3,  # GPIO9 , GPIO25
                      3, 3,  # GPIO11, GPIO8
                      0, 3,  # GND   , GPIO7
                      0, 0,  # I2C   , I2C     #FROM HERE
                      3, 0,  # GPIO5 , GND     #RPI >= B+
                      3, 3,  # GPIO6 , GPIO12
                      3, 0,  # GPIO13, GND
                      3, 3,  # GPIO19, GPIO16
                      3, 3,  # GPIO26, GPIO20
                      0, 3   # GND   , GPIO21
                      ]

GPIO_NAMES = ["3v3", "5v",
              "GPIO2", "5V",
              "GPIO3", "GND",
              "GPIO4", "GPIO14",
              "GND", "GPIO15",
              "GPIO17", "GPIO18",
              "GPIO27", "GND",
              "GPIO22", "GPIO23",
              "3V3", "GPIO24",
              "GPIO10", "GND",
              "GPIO9", "GPIO25",
              "GPIO11", "GPIO8",
              "GND", "GPIO7",
              "I2C", "I2C",
              "GPIO5", "GND",
              "GPIO6", "GPIO12",
              "GPIO13", "GND",
              "GPIO19", "GPIO16",
              "GPIO26", "GPIO20",
              "GND", "GPIO21"
              ]

PIN_TO_GPIO = {'pin14': 22,
               'pin6': 4,
               'pin10': 17,
               'pin21': 25,
               }
GPIO_TO_PIN = dict((v, k) for k, v in PIN_TO_GPIO.items())

BCM = 2


def init():
    """Init GPIO"""
    raise NotImplementedError


def set_pin_value(pin, value):  # pylint: disable=W0613
    """Set arbitrary value to a pin

    This is useful to simulate a state change of pin
    """
    raise NotImplementedError


def setmode(mode):  # pylint: disable=W0613,R0201
    """Simulate set mode"""
    return


def setup(pin, mode, initial=LOW, pull_up_down=PUD_OFF):  # pylint: disable=W0613
    """Set the input or output mode for a specified pin. Mode should be
    either OUT or IN."""
    raise NotImplementedError


def output(pin, value):  # pylint: disable=W0613
    """Set the specified pin the provided high/low value. Value should be
    either HIGH/LOW or a boolean (true = high)."""
    raise NotImplementedError


def input(pin):  # pylint: disable=W0622,W0613
    """Read the specified pin and return HIGH/true if the pin is pulled high,
    or LOW/false if pulled low."""
    raise NotImplementedError


def set_high(pin):
    """Set the specified pin HIGH."""
    output(pin, HIGH)


def set_low(pin):
    """Set the specified pin LOW."""
    output(pin, LOW)


def is_high(pin):
    """Return true if the specified pin is pulled high."""
    return input(pin) == HIGH


def is_low(pin):
    """Return true if the specified pin is pulled low."""
    return input(pin) == LOW


def output_pins(pins):
    """Set output for several pins"""
    for pin, value in iter(pins.items()):
        output(pin, value)


def setup_pins(pins):
    """Setup several pins"""
    for pin, value in iter(pins.items()):
        setup(pin, value)


def input_pins(pins):
    """Get input for several pins"""
    return [input(pin) for pin in pins]


def add_event_detect(pin, edge):  # pylint: disable=R0201
    """Enable edge detection events for a particular GPIO channel. Pin
    should be type IN.  Edge must be RISING, FALLING or BOTH.
    """
    EVENT_DETECTOR[pin] = edge


def remove_event_detect(pin):  # pylint: disable=W0613
    """Remove edge detection for a particular GPIO channel. Pin should be
    type IN.
    """
    raise NotImplementedError


def add_event_callback(pin, callback):  # pylint: disable=R0201
    """Add a callback for an event already defined using add_event_detect().
    Pin should be type IN.
    """
    EVENT_CALLBACK[pin] = callback


def event_detected(pin):  # pylint: disable=W0613
    """Returns True if an edge has occured on a given GPIO. You need to
    enable edge detection using add_event_detect() first. Pin should be
    type IN.
    """
    raise NotImplementedError


def wait_for_edge(pin, edge):  # pylint: disable=W0613
    """Wait for an edge. Pin should be type IN.  Edge must be RISING,
    FALLING or BOTH."""
    raise NotImplementedError


def cleanup(pin=None):  # pylint: disable=W0613
    """Clean up GPIO event detection for specific pin, or all pins if none
    is specified.
    """
    pass


class CommonEventer(Thread):
    """Detect pin state changes"""

    def __init__(self):
        Thread.__init__(self)
        self.old_conf = {}
        self.running = True

    def stop(self):
        """Stop Eventer"""
        self.running = False

    def run(self):
        """Start Eventer"""
        raise NotImplementedError


class Callbacker(Thread):
    """Thread for event callback"""

    def __init__(self, gpio_id):
        Thread.__init__(self)
        self.gpio_id = gpio_id

    def run(self):
        """Run callback"""
        EVENT_CALLBACK[self.gpio_id](self.gpio_id)
