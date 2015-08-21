#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
from datetime import datetime, timedelta
import subprocess


'''
dmesg.py - dmesg with human-readable timestamps
I wrote this code just for fun and then found a similar tool:
https://gist.github.com/saghul/542780
but once wrote - let remains ;)
'''

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '0.1.2015082116'
__maintainer__ = 'Nikolay Gatilov'

TIME_TEMLPATE = "%Y.%m.%d %H:%M:%S"

tsnow = datetime.now()

with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])

uptime_timedelta = timedelta(seconds=uptime_seconds)
tsboot = tsnow - uptime_timedelta

prog = re.compile(r'\[(\d*\.?\d*)\](.*)')

s_out = subprocess.check_output('dmesg').split('\n')

for string in s_out:
    result = prog.match(string)
    if result:
        msgdelta = timedelta(seconds=float(result.group(1)))
        msgtime = tsboot + msgdelta
        print '[%s] %s' % (msgtime.strftime(TIME_TEMLPATE), result.group(2))
