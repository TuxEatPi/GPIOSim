#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='GPIOSim',
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    GPIOSim=GPIOSim.gui:main
    """,
)
