#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess
import re


'''
munin Adaptec raid temperature plugin
If you want Fahrenheit scale instead of Celsuis - change SCALE = 'F'
On the Adaptec 6805 Firmware 5.2-0 (19147) sometimes arcconf return
incorrect temperature -4C or empty string. For fix this bug I ask
the controller again. shit, yes ;(
Last version: https://github.com/eking-go/public-tools
'''

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '0.2.2015070117'
__maintainer__ = 'Nikolay Gatilov'


SCALE = 'C'


def get_temp_status():
    ''' return (temp_celsius, temp_F, status)'''
    #   Temperature                              : 40 C/ 104 F (Normal)
    t_re = re.compile('^\s*Temperature\s*:\s*(\d*).*C/\s(\d*).*\((.*)\).*$')
    while True:
        p = subprocess.Popen("/usr/bin/sudo /usr/StorMan/arcconf GETCONFIG 1 AL",
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True)
        (s_out, s_err) = (p.stdout, p.stderr)
        for line in s_out:
            status = t_re.match(line)
            if status:
                try:
                    return (int(status.group(1)),
                            int(status.group(2)),
                            status.group(3))
                except:
                    pass
    return (0, 0, 'FAIL CHECK ARCCONF: %s' % s_err)

if __name__ == "__main__":  # main
    if len(sys.argv) == 1:
        stat = get_temp_status()
        while stat[0] < 0:
            stat = get_temp_status()
        if SCALE == 'C':
            print 'temp.value %d' % stat[0]
        else:
            print 'temp.value %d' % stat[1]
    elif sys.argv[1] == 'autoconf':
        print 'yes'
    elif sys.argv[1] == 'config':
        print ('graph_title Temperature of RAID-Controller\n'
               'graph_args --base 1000 -l 0\n'
               'graph_vlabel Temperature\n'
               'graph_category Disk\n'
               'graph_order temp\n'
               'graph_info This graph shows the temperature of'
               ' the RAID-Controller.\n'
               'temp.label Temperature C\n'
               'temp.draw LINE1\n')
