#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
NRPE plugin with perfomance data to check maximum
cpu load and steal on VPS via libvirt

It get info from:

* `kvmtop -r 1 --cpu --printer=json`

https://cha87de.github.io/kvmtop/
'''

import json
import subprocess
import sys

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '1.0.2019072014'
__maintainer__ = 'Nikolay Gatilov'
__email__ = 'eking.work@gmail.com'
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


class CpuCheck(object):

    def __init__(self,
                 kvmtopbin='/usr/bin/kvmtop'):
        self.kvmtop = ['sudo']
        self.kvmtop.append(kvmtopbin)
        self.kvmtop.extend(['--runs=1', '--cpu', '--printer=json'])
        self.perfdata = {}
        self.state = OK
        self.comment = []

    def msg(self):
        m = ' '.join(self.comment)
        p = ''
        for i in sorted(self.perfdata.keys()):
            if self.perfdata[i]['perfd']:
                p = "%s, '%s'=%.4f;;;;" % (p, i, self.perfdata[i]['value'])
        if p == '':
            s = m
        else:
            s = '%s|%s' % (m, p[1:])
        if self.state == OK:
            print('CPU state OK:%s\n' % s)
            sys.exit(self.state)
        if self.state == WARNING:
            print('CPU state WARNING:%s\n' % s)
            sys.exit(self.state)
        if self.state == CRITICAL:
            print('CPU state CRITICAL:%s\n' % s)
            sys.exit(self.state)
        if self.state == UNKNOWN:
            print('CPU state UNKNOWN:%s\n' % s)
            sys.exit(self.state)

    def update_state(self,
                     state,
                     comment=None,
                     label=None,
                     value=None,
                     units=None,
                     perfd=False):
        if not (comment is None):
            self.comment.append(comment)
        if not (label is None) and not (value is None):
            self.perfdata[label] = {}
            self.perfdata[label]['value'] = value
            self.perfdata[label]['perfd'] = perfd
            self.perfdata[label]['units'] = units
        if state > self.state:
            self.state = state
        if self.state != OK:
            self.msg()

    def check_kvmtop(self):
        ret = {}
        try:
            p = subprocess.check_output(self.kvmtop,
                                        universal_newlines=True,
                                        stderr=subprocess.STDOUT)
            dl = json.loads(p)['domains']
            ret['max_cpu'] = 0
            ret['max_steal'] = 0
            ret['mc_name'] = ''
            ret['ms_name'] = ''
            for v in dl:
                if v['cpu_total'] >= ret['max_cpu']:
                    ret['max_cpu'] = v['cpu_total']
                    ret['mc_name'] = v['name']
                if v['cpu_steal'] >= ret['max_steal']:
                    ret['max_steal'] = v['cpu_steal']
                    ret['ms_name'] = v['name']
        except Exception as e:
            self.update_state(UNKNOWN,
                              label='Unable to run kvmtop',
                              value=str(e))
        return ret

    def check_cpu(self,
                  max_steal_warn=100,
                  max_steal_crit=101,
                  max_cpu_warn=100,
                  max_cpu_crit=101):
        cpu = self.check_kvmtop()
        msg = ' Domain %s has STEAL %d %%, Domain %s has CPU usage %d %%' % (cpu['ms_name'],
                                                                             cpu['max_steal'],
                                                                             cpu['mc_name'],
                                                                             cpu['max_cpu'])
        if cpu['max_cpu'] >= max_cpu_crit:
            self.update_state(CRITICAL,
                              comment=msg,
                              label='max_cpu_usage',
                              value=cpu['max_cpu'],
                              units='%',
                              perfd=True)
        elif cpu['max_cpu'] >= max_cpu_warn:
            self.update_state(WARNING,
                              comment=msg,
                              label='max_cpu_usage',
                              value=cpu['max_cpu'],
                              units='%',
                              perfd=True)
        else:
            self.update_state(OK,
                              comment=msg,
                              label='max_cpu_usage',
                              value=cpu['max_cpu'],
                              units='%',
                              perfd=True)
        if cpu['max_steal'] >= max_steal_crit:
            self.update_state(CRITICAL,
                              label='max_steal_usage',
                              value=cpu['max_steal'],
                              units='%',
                              perfd=True)
        elif cpu['max_steal'] >= max_steal_warn:
            self.update_state(WARNING,
                              label='max_steal_usage',
                              value=cpu['max_steal'],
                              units='%',
                              perfd=True)
        else:
            self.update_state(OK,
                              label='max_steal_usage',
                              value=cpu['max_steal'],
                              units='%',
                              perfd=True)


if __name__ == '__main__':  # main
    import argparse
    opt = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                  epilog='version: %s' % __version__)
    opt.add_argument('--kvmtop',
                     dest='kvmtop',
                     default='/usr/bin/kvmtop',
                     help='Full path to kvmtop binary (default: %(default)s)')
    opt.add_argument('--max_steal_warn',
                     dest='max_steal_warn',
                     default=100,
                     type=int,
                     help='Maximum steal (on all VPS) WARNING value (default: %(default)s)')
    opt.add_argument('--max_steal_crit',
                     dest='max_steal_crit',
                     default=101,
                     type=int,
                     help='Maximum steal (on all VPS) CRITICAL value (default: %(default)s)')
    opt.add_argument('--max_cpu_warn',
                     dest='max_cpu_warn',
                     default=100,
                     type=int,
                     help='Maximum cpu (on all VPS) WARNING value (default: %(default)s)')
    opt.add_argument('--max_cpu_crit',
                     dest='max_cpu_crit',
                     default=101,
                     type=int,
                     help='Maximum cpu (on all VPS) CRITICAL value (default: %(default)s)')
    options = opt.parse_args()
    cc = CpuCheck(kvmtopbin=options.kvmtop)
    cc.check_cpu(max_steal_warn=options.max_steal_warn,
                 max_steal_crit=options.max_steal_crit,
                 max_cpu_warn=options.max_cpu_warn,
                 max_cpu_crit=options.max_cpu_crit)
    cc.msg()
