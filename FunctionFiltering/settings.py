#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

"""
import sys

from pathlib import Path

# replace with your IDA path
IDA64_PATH = Path('/idapro-7.3/idat64')
IDA_PATH = Path('/idapro-7.3/idat')

if not IDA_PATH.exists() or not IDA64_PATH.exists():
    raise FileNotFoundError('Can not find ida, please check your ida path')


PLATFORM = sys.platform
if PLATFORM.startswith('linux'):
    IS_LINUX = True
else:
    IS_LINUX = False
