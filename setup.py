#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='tuxeatpi',
    entry_points="""
    [console_scripts]
    GPIOSim=GPIOSim.gui:main
    """,
)
