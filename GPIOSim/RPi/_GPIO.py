#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# GPIOSim
#
# Bob Vann - http://bobvann.noip.me
#
# https://github.com/bobvann/GPIOSim
# 
# Requires Python 3

import os, tempfile,signal
from configparser import RawConfigParser
import time
from threading import Thread, Lock




# Set dict
_event_detector = {}
_event_callback = {}

class Gpio(object):

    OUT     = 2
    IN      = 1
    HIGH    = 1
    LOW     = 0

    RISING      = 1
    FALLING     = 2
    BOTH        = 3

    PUD_OFF  = 0
    PUD_DOWN = 1
    PUD_UP   = 2

    # TODO find true value

    GPIO_STATE_DEFAULT = [
            0, 0,  #3v3   , 5v
            3, 0,  #GPIO2 , 5V
            3, 0,  #GPIO3 , GND 
            3, 3,  #GPIO4 , GPIO14
            0, 3,  #GND   , GPIO15
            3, 3,  #GPIO17, GPIO18
            3, 0,  #GPIO27, GND
            3, 3,  #GPIO22, GPIO23
            0, 3,  #3V3   , GPIO24
            3, 0,  #GPIO10, GND
            3, 3,  #GPIO9 , GPIO25
            3, 3,  #GPIO11, GPIO8
            0, 3,  #GND   , GPIO7
            0, 0,  #I2C   , I2C     #FROM HERE
            3, 0,  #GPIO5 , GND     #RPI >= B+
            3, 3,  #GPIO6 , GPIO12
            3, 0,  #GPIO13, GND
            3, 3,  #GPIO19, GPIO16
            3, 3,  #GPIO26, GPIO20
            0, 3   #GND   , GPIO21
        ]


    GPIO_NAMES = [
        "3v3","5v",
        "GPIO2","5V",
        "GPIO3","GND",
        "GPIO4","GPIO14",
        "GND","GPIO15",
        "GPIO17","GPIO18",
        "GPIO27","GND",
        "GPIO22","GPIO23",
        "3V3","GPIO24",
        "GPIO10","GND",
        "GPIO9","GPIO25",
        "GPIO11","GPIO8",
        "GND","GPIO7",
        "I2C","I2C",
        "GPIO5","GND",
        "GPIO6","GPIO12",
        "GPIO13","GND",
        "GPIO19","GPIO16",
        "GPIO26","GPIO20",
        "GND","GPIO21"
    ]


    PIN_TO_GPIO = {'pin14': 22,
                   'pin6': 4,
                   'pin10': 17,
                   'pin21': 25,
                  }
    GPIO_TO_PIN = dict((v, k) for k, v in PIN_TO_GPIO.items())


    def __init__(self):
        # set 
        self.BCM = 2
        

        # set work file and dir as params
        self.work_dir = os.path.join(tempfile.gettempdir(), "GPIOSim")
        self.work_file = os.path.join(self.work_dir, "pins.ini")
        self.parser = RawConfigParser()
        self.lock = Lock()

        # create folder
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

        # read file
        self.parser.read(self.work_file)
        # Set default values
        for i in range(0,40):
            if not self.parser.has_section("pin" + str(i)):
                self.parser.add_section("pin" + str(i))

            self.parser.set("pin" + str(i), "state", str(self.GPIO_STATE_DEFAULT[i]))
            self.parser.set("pin" + str(i), "value", "0")
        # write file
        self._write()

        # Eventer
        self.eventer = Eventer(self)
        self.eventer.start()

    def _read(self):
        """Read config file"""
        self.parser.read(self.work_file)

    def _write(self):
        """Write config"""
        print("QQQQQQQQQQQQQQQQQ")
        self.lock.acquire()
        with open(self.work_file, 'w') as configfile:
            self.parser.write(configfile)
        self.lock.release()

    def set_pin_value(self, pin, value):
        """Set arbitrary value to a pin

        This is useful to simulate a state change of pin
        """
        self._read()
        self.parser.set(pin, "value", value)
        self._write()

    def setmode(self, mode):
        """Simulate set mode"""
        return

    def setup(self, pin, mode, initial=LOW, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUT or IN."""
        self._read()

        pin = self.GPIO_NAMES.index("GPIO" + str(pin))

        if self.parser.getint("pin" + str(pin), "state") == 0:
            raise Exception

        self.parser.set("pin" + str(pin), "state", str(mode))
        if mode == self.OUT:
            self.parser.set("pin" + str(mode), "value", "0")

        self._write()
        # FIXME This is really ugly !!!!!
        # pid = os.popen("ps ax |grep ':[0-9][0-9] GPIOSim'").read()
        # if pid != '':
        #    os.kill(int(pid), signal.SIGUSR1)


    def output(self, pin, value):
        """Set the specified pin the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high)."""
        self._read()

        pin = self.GPIO_NAMES.index("GPIO" + str(pin))

        if self.parser.getint("pin" + str(pin), "state") != self.OUT:
            raise Exception

        self.parser.set("pin" + str(pin), "value", str(value))

        self._write()
        # FIXME This is really ugly !!!!!
        # pid = os.popen("ps ax |grep ':[0-9][0-9] GPIOSim'").read()
        # if pid != '':
        #    os.kill(int(pid), signal.SIGUSR1)


    def input(self, pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low."""
        pin = GPIO_NAMES.index("GPIO" + str(pin))

        self._read()
        return self.parser.getint("pin"+str(pin),"value")


    def set_high(self, pin):
        """Set the specified pin HIGH."""
        self.output(pin, HIGH)

    def set_low(self, pin):
        """Set the specified pin LOW."""
        self.output(pin, LOW)

    def is_high(self, pin):
        """Return true if the specified pin is pulled high."""
        return self.input(pin) == HIGH

    def is_low(self, pin):
        """Return true if the specified pin is pulled low."""
        return self.input(pin) == LOW


    # Basic implementation of multiple pin methods just loops through pins and
    # processes each one individually. This is not optimal, but derived classes can
    # provide a more optimal implementation that deals with groups of pins
    # simultaneously.
    # See MCP230xx or PCF8574 classes for examples of optimized implementations.

    def output_pins(self, pins):
        for pin, value in iter(pins.items()):
            self.output(pin, value)

    def setup_pins(self, pins):
        for pin, value in iter(pins.items()):
            self.setup(pin, value)

    def input_pins(self, pins):
        return [self.input(pin) for pin in pins]


    def add_event_detect(self, pin, edge):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.
        """
        _event_detector[pin] = edge

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        raise NotImplementedError

    def add_event_callback(self, pin, callback):
        """Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.
        """
        _event_callback[pin] = callback

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.  You need to 
        enable edge detection using add_event_detect() first.   Pin should be 
        type IN.
        """
        raise NotImplementedError

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH."""
        raise NotImplementedError

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none 
        is specified.
        """
        if os.path.exists(self.work_file):
            os.remove(self.work_file)
        if os.path.exists(self.work_dir):
            os.removedirs(self.work_dir)
        self.eventer.stop()
        try:
            self.lock.release()
        except RuntimeError:
            pass


# helper functions useful to derived classes

def _validate_pin(pin):
    # Raise an exception if pin is outside the range of allowed values.
    check()
    if (pin not in PINS_A) and (pin not in PINS_B):
        raise ValueError('Invalid GPIO value, must be between A0 AND A7 or between B0 AND B7')

# no idea what is this and if I should iplement it
#def _bit2( src, bit, val):
    #bit = 1 << bit
    #return (src | bit) if val else (src & ~bit)


class Eventer(Thread):

    def __init__(self, gpio):
        Thread.__init__(self)
        self.old_conf = {}
        self.running = True
        self.gpio = gpio

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
  #          try:
                self.gpio._read()
                for key, section in self.gpio.parser.items():
                    # TODO find what means state
                    if self.old_conf.get(key, {}).get('value') is not None and section.getint('state') == 1:
                        # RISING and BOTH
                        if self.old_conf[key]['value'] == 0 and section.getint('value') == 1:
                            if _event_detector[self.gpio.PIN_TO_GPIO[key]] in [self.gpio.RISING, self.gpio.BOTH]:
                                callback = Callbacker(self.gpio.PIN_TO_GPIO[key])
                                callback.start()
                        # FALLING and BOTH
                        if self.old_conf[key]['value'] == 1 and section.getint('value') == 0:
                            if _event_detector[self.gpio.PIN_TO_GPIO[key]] in [self.gpio.FALLING, self.gpio.BOTH]:
                                callback = Callbacker(self.gpio.PIN_TO_GPIO[key])
                                callback.start()
                    # save values
                    if self.old_conf.get(key) is None:
                        self.old_conf[key] = {}
                    self.old_conf[key]['value'] = section.getint('value')
                    self.old_conf[key]['state'] = section.getint('state')
                # Sleep
                time.sleep(1)
 #           except Exception:
#                pass

class Callbacker(Thread):

    def __init__(self, gpio_id):
        Thread.__init__(self)
        self.gpio_id = gpio_id

    def run(self):
        _event_callback[self.gpio_id](self.gpio_id)
