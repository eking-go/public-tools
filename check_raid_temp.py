#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
nagios check Adaptec raid temperature plugin
On the Adaptec 6805 Firmware 5.2-0 (19147) sometimes arcconf return
incorrect temperature -4C or empty string. For fix this bug I ask
the controller again. shit, yes ;(
Last version: https://github.com/eking-go/public-tools
'''

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '0.1.2015070117'
__maintainer__ = 'Nikolay Gatilov'

import sys
import subprocess
import re
import argparse


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
    check_status = 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wc', help=('Warning Celsius'), type=int)
    parser.add_argument('--cc', help=('Critical Celsius'), type=int)
    parser.add_argument('--wf', help=('Warning Fahrenheit'), type=int)
    parser.add_argument('--cf', help=('Critical Fahrenheit'), type=int)
    args = parser.parse_args()
    stat = get_temp_status()

    if stat[2] != 'Normal':
        check_status = 2

    if args.wc and args.wc < stat[0]:
        check_status = 1
    elif args.cc and args.cc < stat[0]:
        check_status = 2

    if args.wf and args.wf < stat[1]:
        check_status = 1
    elif args.cf and args.cf < stat[1]:
        check_status = 2

    print 'Adaptec Raid Temperature %d C / %d F / status: %s' % (stat[0],
                                                                 stat[1],
                                                                 stat[2])
    sys.exit(check_status)
