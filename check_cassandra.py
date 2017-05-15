#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
NRPE plugin with perfomance data for check cassandra node state.

It get info from:

* `nodetool info`
http://docs.datastax.com/en/archived/cassandra/3.x/cassandra/tools/toolsInfo.html
https://cassandra.apache.org/doc/latest/tools/nodetool/info.html

* `nodetool proxyhistograms`
http://docs.datastax.com/en/archived/cassandra/3.x/cassandra/tools/toolsProxyHistograms.html
https://cassandra.apache.org/doc/latest/tools/nodetool/proxyhistograms.html

* `nodetool tablestats`
http://docs.datastax.com/en/archived/cassandra/3.x/cassandra/tools/toolsTablestats.html
https://cassandra.apache.org/doc/latest/tools/nodetool/tablestats.html

If you do not use --keyspace option it checking node state with
info and proxyhistograms, but with --keyspace option it checking
only nodetool tablestats
'''

import re
import subprocess
import sys

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '1.0.2017051514'
__maintainer__ = 'Nikolay Gatilov'
__email__ = 'eking.work@gmail.com'
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


class CasCheck:

    def __init__(self,
                 nodetoolbin='nodetool',
                 host=None,
                 port=None,
                 user=None,
                 password=None,
                 full_check=True):
        self.nodetool = []
        self.nodetool.append(nodetoolbin)
        if user is not None:
            self.nodetool.extend(['--username', user])
        if host is not None:
            self.nodetool.extend(['--host', host])
        if port is not None:
            self.nodetool.extend(['--port', port])
        if password is not None:
            self.nodetool.extend(['--password', password])
        self.perfdata = {}
        self.state = OK
        self.full_check = full_check

    def msg(self):
        m = ''
        p = ''
        for i in sorted(self.perfdata.keys()):
            if not (self.perfdata[i]['units'] is None):
                su = '(%s)' % self.perfdata[i]['units']
            else:
                su = ''
            m = "%s; %s: %s%s" % (m, i, str(self.perfdata[i]['value']), su)
            if self.perfdata[i]['perfd']:
                p = "%s, '%s'=%.4f;;;;" % (p, i, self.perfdata[i]['value'])
        if p == '':
            s = m[1:]
        else:
            s = '%s|%s' % (m[1:], p[1:])
        if self.state == OK:
            print('Cassandra node state OK:%s\n' % s)
            sys.exit(self.state)
        if self.state == WARNING:
            print('Cassandra node state WARNING:%s\n' % s)
            sys.exit(self.state)
        if self.state == CRITICAL:
            print('Cassandra node state CRITICAL:%s\n' % s)
            sys.exit(self.state)
        if self.state == UNKNOWN:
            print('Cassandra node state UNKNOWN:%s\n' % s)
            sys.exit(self.state)

    def update_state(self,
                     state,
                     label=None,
                     value=None,
                     units=None,
                     perfd=False):
        if not (label is None) and not (value is None):
            self.perfdata[label] = {}
            self.perfdata[label]['value'] = value
            self.perfdata[label]['perfd'] = perfd
            self.perfdata[label]['units'] = units
        if state > self.state:
            self.state = state
        if self.state != OK and not self.full_check:
            self.msg()

    def check_nodetool(self, a):
        nodetool = list(self.nodetool)
        nodetool.append(a)
        try:
            p = subprocess.check_output(nodetool,
                                        universal_newlines=True,
                                        stderr=subprocess.STDOUT)
            return p.split('\n')
        except Exception as e:
            self.update_state(UNKNOWN,
                              label='Unable to run nodetool',
                              value=str(e))
            return []

    def check_info(self,
                   without_gossip=False,
                   without_thrift=False,
                   without_native=False,
                   heap_used_coeff=1):
        for line in self.check_nodetool('info'):
            s = re.search('Gossip active\s*:\s*(\w*)', line)
            if s:
                if not without_gossip or s.group(1) == 'true':
                    self.update_state(OK, 'Gossip active', s.group(1))
                else:
                    self.update_state(CRITICAL, 'Gossip active', s.group(1))
            s = re.search('Thrift active\s*:\s*(\w*)', line)
            if s:
                if not without_thrift or s.group(1) == 'true':
                    self.update_state(OK, 'Thrift active', s.group(1))
                else:
                    self.update_state(CRITICAL, 'Thrift active', s.group(1))
            s = re.search('Native Transport active\s*:\s*(\w*)', line)
            if s:
                if not without_native or s.group(1) == 'true':
                    self.update_state(OK,
                                      'Native Transport active',
                                      s.group(1))
                else:
                    self.update_state(CRITICAL,
                                      'Native Transport active',
                                      s.group(1))
            s = re.search('Load\s*:\s*([\d,.]*)\s*(\w*)', line)
            if s:
                val = float(s.group(1).replace(',', '.'))
                self.update_state(OK,
                                  'Load data',
                                  value=val,
                                  units=s.group(2),
                                  perfd=True)
            s = re.search('Heap Memory\s*\((\w*)\)\s*:\s*([\d,.]*)\s*/\s*([\d,.]*)',
                          line)
            if s:
                heap_unit = s.group(1)
                heap_used = float(s.group(2).replace(',', '.'))
                heap_total = float(s.group(3).replace(',', '.'))
                self.update_state(OK,
                                  'Heap Memory Total',
                                  value=heap_total,
                                  units=heap_unit,
                                  perfd=True)
                if heap_used >= heap_total*heap_used_coeff:
                    self.update_state(CRITICAL,
                                      'Heap Memory Used',
                                      heap_used,
                                      heap_unit,
                                      perfd=True)
                else:
                    self.update_state(OK,
                                      'Heap Memory Used',
                                      heap_used,
                                      heap_unit,
                                      perfd=True)
            s = re.search('Off Heap Memory\s*\((\w*)\)\s*:\s*([\d,.]*)',
                          line)
            if s:
                oheap_unit = s.group(1)
                oheap_used = float(s.group(2).replace(',', '.'))
                self.update_state(OK,
                                  'Off Heap Memory',
                                  oheap_used,
                                  oheap_unit,
                                  perfd=True)

    def check_proxyhistograms(self,
                              cpname='99%',
                              coordinator_RLW=None,
                              coordinator_WLW=None,
                              coordinator_RLC=None,
                              coordinator_WLC=None):
        for line in self.check_nodetool('proxyhistograms'):
            la = line.split()
            if len(la) > 0 and cpname == la[0]:
                rl = float(la[1].replace(',', '.'))
                wl = float(la[2].replace(',', '.'))
                if coordinator_WLC is not None and wl >= coordinator_WLC:
                    self.update_state(CRITICAL,
                                      'Inter-node write latency %s' % cpname,
                                      wl,
                                      units='micros',
                                      perfd=True)
                elif coordinator_WLW is not None and wl >= coordinator_WLW:
                    self.update_state(WARNING,
                                      'Inter-node write latency %s' % cpname,
                                      wl,
                                      units='micros',
                                      perfd=True)
                else:
                    self.update_state(OK,
                                      'Inter-node write latency %s' % cpname,
                                      wl,
                                      units='micros',
                                      perfd=True)
                if coordinator_RLC is not None and rl >= coordinator_RLC:
                    self.update_state(CRITICAL,
                                      'Inter-node read latency %s' % cpname,
                                      rl,
                                      units='micros',
                                      perfd=True)
                elif coordinator_RLW is not None and rl >= coordinator_RLW:
                    self.update_state(WARNING,
                                      'Inter-node read latency %s' % cpname,
                                      rl,
                                      units='micros',
                                      perfd=True)
                else:
                    self.update_state(OK,
                                      'Inter-node read latency %s' % cpname,
                                      rl,
                                      units='micros',
                                      perfd=True) 

    def check_tablestats(self,
                         keyspace=None,
                         r_l_w=None,
                         w_l_w=None,
                         r_l_c=None,
                         w_l_c=None):
        '''tablestats| egrep "Keyspace|Latency|Count"
           Keyspace : system_traces
                   Read Count: 0
                   Read Latency: NaN ms.
                   Write Count: 0
                   Write Latency: NaN ms.
        '''
        keyspace_r = re.compile('Keyspace\s*:\s*(\w*)')
        read_c_r = re.compile('\s*Read Count:\s*(\d*)')
        read_l_r = re.compile('\s*Read Latency:\s*([Na\d.]*)\s*ms\.')
        write_c_r = re.compile('\s*Write Count:\s*(\d*)')
        write_l_r = re.compile('\s*Write Latency:\s*([Na\d.]*)\s*ms\.')
        for line in self.check_nodetool('tablestats'):
            ksr = keyspace_r.search(line)
            if ksr:
                ks = ksr.group(1)
                continue
            rcr = read_c_r.search(line)
            if rcr:
                rc = int(rcr.group(1))
                continue
            rlr = read_l_r.search(line)
            if rlr:
                rlr_t = rlr.group(1)
                if rlr_t != 'NaN':
                    rl = float(rlr_t)
                else:
                    rl = rlr_t
                continue
            wcr = write_c_r.search(line)
            if wcr:
                wc = int(wcr.group(1))
                continue
            wlr = write_l_r.search(line)
            if wlr:
                wlr_t = wlr.group(1)
                if wlr_t != 'NaN':
                    wl = float(wlr_t)
                else:
                    wl = wlr_t
                if not (keyspace is None) and ks != keyspace:
                    continue
                else:
                    if not (r_l_c is None) and rl != 'NaN' and rl >= r_l_c:
                        self.update_state(CRITICAL,
                                          'Read Latency for %s' % ks,
                                          rl,
                                          units='ms',
                                          perfd=True)
                    elif not (w_l_c is None) and wl != 'NaN' and wl >= w_l_c:
                        self.update_state(CRITICAL,
                                          'Write Latency for %s' % ks,
                                          wl,
                                          units='ms',
                                          perfd=True)
                    elif not (r_l_w is None) and rl != 'NaN' and rl >= r_l_w:
                        self.update_state(WARNING,
                                          'Read Latency for %s' % ks,
                                          rl,
                                          units='ms',
                                          perfd=True)
                    elif not (w_l_w is None) and wl != 'NaN' and wl >= w_l_w:
                        self.update_state(WARNING,
                                          'Write Latency for %s' % ks,
                                          wl,
                                          units='ms',
                                          perfd=True)
                    else:
                        if rl != 'NaN':
                            self.update_state(OK,
                                              'Read Latency for %s' % ks,
                                              rl,
                                              units='ms',
                                              perfd=True)
                        else:
                            self.update_state(OK,
                                              'Read Latency for %s' % ks,
                                              'NaN',
                                              units='ms')
                        if wl != 'NaN':
                            self.update_state(OK,
                                              'Write Latency for %s' % ks,
                                              wl,
                                              units='ms',
                                              perfd=True)
                        else:
                            self.update_state(OK,
                                              'Write Latency for %s' % ks,
                                              'NaN',
                                              units='ms')
                        self.update_state(OK,
                                          'Write Counter for %s' % ks,
                                          wc,
                                          perfd=True)
                        self.update_state(OK,
                                          'Read Counter for %s' % ks,
                                          rc,
                                          perfd=True)


if __name__ == '__main__':  # main
    import argparse
    opt = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                  epilog='version: %s' % __version__)
    opt.add_argument('--nodetool',
                     dest='nodetool',
                     default='nodetool',
                     help='Full path to nodetool binary (default: %(default)s)')
    opt.add_argument('--host',
                     dest='host',
                     default=None,
                     help='Host to connect (default: %(default)s - '
                          'not use argument with nodetool)')
    opt.add_argument('--port',
                     dest='port',
                     default=None,
                     help='Port to connect (default: %(default)s - '
                          'not use argument with nodetool)')
    opt.add_argument('--user',
                     dest='user',
                     default=None,
                     help='Cassandra user to connect (default: %(default)s - '
                          'not use argument with nodetool)')
    opt.add_argument('--password',
                     dest='password',
                     default=None,
                     help='Cassandra password to connect (default: %(default)s'
                          ' - not use argument with nodetool)')
    opt.add_argument('--hcc',
                     dest='hcc',
                     default=1,
                     help='0..1 - critical %% using HEAP '
                          '(default: %(default)s)')
    opt.add_argument('--without_gossip',
                     dest='without_gossip',
                     action='store_true',
                     help=('If used (True) - disabled gossip is not critical'
                           ' (default: %(default)s)'))
    opt.add_argument('--without_thrift',
                     dest='without_thrift',
                     action='store_true',
                     help=('If used (True) - disabled thrift is not critical'
                           ' (default: %(default)s)'))
    opt.add_argument('--without_native',
                     dest='without_native',
                     action='store_true',
                     help=('If used (True) - disabled native protocol is not '
                           'critical (default: %(default)s)'))
    opt.add_argument('--fast_check',
                     dest='full_check',
                     action='store_false',
                     help=('If used (False) - do not check all - exit and '
                           'return the status as soon as the [W/C/U] value '
                           'is received (default: %(default)s)'))
    opt.add_argument('--coordinator_percentile',
                     dest='coordinator_percentile',
                     default='99%',
                     help='coordinator percentile, for checking inter node '
                          'communication latency, see nodetool '
                          'proxyhistograms (default: %(default)s)')
    opt.add_argument('--coordinator_RLW',
                     dest='coordinator_RLW',
                     default=None,
                     help='Inter-node communication read latency (from '
                          'coordinator, micros) WARNING value, None - '
                          'Does not cause a change in state '
                          '(default: %(default)s)')
    opt.add_argument('--coordinator_RLC',
                     dest='coordinator_RLC',
                     default=None,
                     help='Inter-node communication read latency (from '
                          'coordinator, micros) CRITICAL value, None - '
                          'Does not cause a change in state'
                          ' (default: %(default)s)')
    opt.add_argument('--coordinator_WLW',
                     dest='coordinator_WLW',
                     default=None,
                     help='Inter-node communication write latency (from '
                          'coordinator, micros) WARNING value, None - '
                          'Does not cause a change in state'
                          ' (default: %(default)s)')
    opt.add_argument('--coordinator_WLC',
                     dest='coordinator_WLC',
                     default=None,
                     help='Inter-node communication write latency (from '
                          'coordinator, micros) CRITICAL value, None - '
                          'Does not cause a change in state'
                          ' (default: %(default)s)')
    opt.add_argument('--keyspace',
                     dest='keyspace',
                     default=None,
                     help='Keyspace for which to check read/write latency,'
                          ' see nodetool tablestats. ALL - check all '
                          'keyspaces (default: %(default)s)')
    opt.add_argument('--ks_read_latency_w',
                     dest='ks_read_latency_w',
                     default=None,
                     help='Keyspace read latency WARNING value '
                          'None - Does not cause a change in state'
                          ' (default: %(default)s)')
    opt.add_argument('--ks_read_latency_c',
                     dest='ks_read_latency_c',
                     default=None,
                     help='Keyspace read latency CRITICAL value '
                          'None - Does not cause a change in state'
                          ' (default: %(default)s)')
    opt.add_argument('--ks_write_latency_w',
                     dest='ks_write_latency_w',
                     default=None,
                     help='Keyspace write latency WARNING value '
                          'None - Does not cause a change in state'
                          ' (default: %(default)s)')
    opt.add_argument('--ks_write_latency_c',
                     dest='ks_write_latency_c',
                     default=None,
                     help='Keyspace write latency CRITICAL value '
                          'None - Does not cause a change in state'
                          ' (default: %(default)s)')

    options = opt.parse_args()
    cs = CasCheck(nodetoolbin=options.nodetool,
                  host=options.host,
                  port=options.port,
                  user=options.user,
                  password=options.password,
                  full_check=options.full_check)
    if options.keyspace is None:
        cs.check_info(without_gossip=options.without_gossip,
                      without_thrift=options.without_thrift,
                      without_native=options.without_native,
                      heap_used_coeff=options.hcc)
        cs.check_proxyhistograms(cpname=options.coordinator_percentile,
                                 coordinator_RLW=options.coordinator_RLW,
                                 coordinator_WLW=options.coordinator_WLW,
                                 coordinator_RLC=options.coordinator_RLC,
                                 coordinator_WLC=options.coordinator_WLC)
    else:
        if options.keyspace == 'ALL':
            ks = None
        else:
            ks = options.keyspace
        cs.check_tablestats(keyspace=ks,
                            r_l_w=options.ks_read_latency_w,
                            w_l_w=options.ks_write_latency_w,
                            r_l_c=options.ks_read_latency_c,
                            w_l_c=options.ks_write_latency_c)
    cs.msg()
