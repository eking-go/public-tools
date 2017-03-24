#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Manage Postfix queue and parse logs.
If defined option --regex (and it not Null)
- script is parse logs, otherwise it working
with mail queue.
Date and time format - %Y-%m-%d %H:%M:%S  (ISO format)
'''

import re
import os
import fnmatch
import gzip
import subprocess
import datetime
import sys
from multiprocessing import Pool

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '1.0.2017032412'
__maintainer__ = 'Nikolay Gatilov'
__email__ = 'eking.work@gmail.com'


class Postfix:
    '''Class to parse log files and postfix queue '''

    def __init__(self,
                 mailq='mailq',
                 postsuper='postsuper',
                 log_mask='mail.info*',
                 log_dir='/var/log',
                 multiprocess=True,
                 noindex=False):
        '''You can set up full path to binary files and logs, default is:
           mailq='mailq', postsuper='postsuper',
           log_mask='mail.info*', log_dir='/var/log'
        '''
        self.mail_reg = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.*[a-zA-Z0-9-.]*|MAILER-DAEMON'
        self.log_mask = log_mask
        self.log_dir = log_dir
        self.mailq = mailq
        self.postsuper = postsuper
        self.postfixloglinereg = '.* postfix.*: (\w+): .*'
        self.multiprocess = multiprocess
        self.noindex = noindex

    def getFiles(self):
        '''Get list of log (rotated), may be gzipped) files '''
        matches = []
        for root, dirnames, filenames in os.walk(self.log_dir):
            for filename in fnmatch.filter(filenames, self.log_mask):
                matches.append(os.path.join(root, filename))
        return matches

    def getFileHandler(self, path):
        '''Get opened file handler or string.io (like file)
           argument to this function - the full path to the file'''
        if path[-3:] == '.gz':
            try:
                return gzip.open(path, mode='rb')
            except Exception as e:
                print(str(e))
                return None
        else:
            try:
                return open(path, mode='rb')
            except Exception as e:
                print(str(e))
                return None

    def getPostfixMailLogByID1(self, fh):
        '''argument to this function is tuple (f, r):
           f - full path to log file
           r - list of the Mail ID which must be found in log
           This is first phase of parsing logs;
           return dict MsgID: list of log lines
        '''
        f = self.getFileHandler(fh[0])
        if f is None:
            return None
        postfixline = re.compile(self.postfixloglinereg)
        p = {}
        for line in f:
            line = line.decode('utf-8')
            plr = postfixline.match(line)
            if plr:
                mid = plr.group(1)
                if mid in fh[1]:
                    if mid not in p.keys():
                        p[mid] = list()
                    p[mid].append(line)
        f.close()
        return p

    def getPostfixMailLogsByID(self, idlist):
        '''Return dict (keys is MsgID) of list of strings from log file
           correspond to this message - from All log files
        '''
        MIL = []
        GF = self.getFiles()
        for f in GF:
            MIL.append((f, idlist))
        if self.multiprocess:
            PILL = Pool().map(self.getPostfixMailLogByID1, MIL)
        else:
            PILL = map(self.getPostfixMailLogByID1, MIL)
        p = {}
        for pool_res in PILL:
            if pool_res is None:
                continue
            for msg in pool_res.keys():
                if msg not in p.keys():
                    p[msg] = list()
                p[msg].extend(pool_res[msg])
        return p

    def getPostfixMLIndexAndRegex(self, fr):
        '''This method parse postfix log file an return index by
           Postfix_mail_id as dictionary {MID: [seek_pos,]}
           and dictionary {regex: [MID]}
        '''
        f = self.getFileHandler(fr[0])
        if f is None:
            return ((fr[0], {}), {})
        postfixline = re.compile(self.postfixloglinereg)
        reg_id_d = {}
        id_seek_d = {}
        rlist = {}
        for i in fr[1]:
            rstr = '(.*%s.*)' % i
            rlist[i] = re.compile(rstr)
        fpos = 0
        for line in f:
            line = line.decode('utf-8')
            plr = postfixline.match(line)
            if plr:
                PMsgID = plr.group(1)
                if not self.noindex:
                    if PMsgID not in id_seek_d.keys():
                        id_seek_d[PMsgID] = []
                    id_seek_d[PMsgID].append(fpos)
                for reg in fr[1]:
                    if rlist[reg].match(line):
                        if reg not in reg_id_d.keys():
                            reg_id_d[reg] = []
                        reg_id_d[reg].append(PMsgID)
            fpos = f.tell()
        f.close()
        return ((fr[0], id_seek_d), reg_id_d)

    def getPostfixMLLines(self, fs):
        '''
        return dict {reg: {MailID: [logStrings, ]}}
        '''
        f = self.getFileHandler(fs[0])
        if f is None:
            return {}
        reg_d = {}
        for fpos in sorted(fs[1].keys()):
            f.seek(fpos)
            line = f.readline().decode('utf-8')
            for reg in fs[1][fpos]:
                if reg not in reg_d.keys():
                    reg_d[reg] = {}
                for mid in fs[1][fpos][reg]:
                    if mid not in reg_d[reg].keys():
                        reg_d[reg][mid] = []
                    reg_d[reg][mid].append(line)
        f.close()
        return reg_d

    def getPostfixMailLogs(self, r):
        '''Return dict (keys is regex) of dict with keys - Postfix message ID
           and list of strings from log file with this message - from All log
           files
        '''
        fr = []
        gf = self.getFiles()
        for f in gf:
            fr.append((f, r))
        if self.multiprocess:
            res_l = Pool().map(self.getPostfixMLIndexAndRegex, fr)
        else:
            res_l = list(map(self.getPostfixMLIndexAndRegex, fr))
        reg_d = {}
        for i in res_l:
            for reg in i[1].keys():
                if reg not in reg_d.keys():
                    reg_d[reg] = []
                reg_d[reg].extend(i[1][reg])
                reg_d[reg] = list(set(reg_d[reg]))
        if self.noindex:
            reg_dr = {}
            for reg in reg_d.keys():
                reg_dr[reg] = self.getPostfixMailLogsByID(reg_d[reg])
            return reg_dr
        fs = []
        for i in res_l:
            file_path = i[0][0]
            seek_d = {}
            for mid in i[0][1].keys():
                for reg in reg_d.keys():
                    if mid in reg_d[reg]:
                        for sid in i[0][1][mid]:
                            if sid not in seek_d.keys():
                                seek_d[sid] = {}
                            if reg not in seek_d[sid].keys():
                                seek_d[sid][reg] = []
                            seek_d[sid][reg].append(mid)
            if seek_d != {}:
                fs.append((file_path, seek_d))
        if self.multiprocess:
            res_l = Pool().map(self.getPostfixMLLines, fs)
        else:
            res_l = map(self.getPostfixMLLines, fs)
        reg_d = {}
        for i in res_l:
            for reg in i.keys():
                if reg not in reg_d.keys():
                    reg_d[reg] = {}
                for mid in i[reg].keys():
                    if mid not in reg_d[reg].keys():
                        reg_d[reg][mid] = []
                    reg_d[reg][mid].extend(i[reg][mid])
        return reg_d

    def dropMessage(self, pmid):
        '''Drop message from postfix queue, return tuple
        (stdin, stderr, exception(as string))'''
        s = ''
        p = subprocess.Popen([self.postsuper, '-d', pmid],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
        try:
            p.wait(timeout=10)
        except Exception as e:
            s = str(e)
        return (p.stdout.read(), p.stderr.read(), s)

    def isFilter(self, rec, mindate, maxdate, from_regex, to_regex):
        if 'time' in rec.keys():
            if mindate is not None and rec['time'] < mindate:
                return False
            if maxdate is not None and rec['time'] > maxdate:
                return False
        else:
            if mindate is not None or maxdate is not None:
                return False
        if 'from' in rec.keys():
            if from_regex is not None:
                frc = re.compile(from_regex)
                if not frc.match(rec['from']):
                    return False
        else:
            if from_regex is not None:
                return False
        if 'to' in rec.keys():
            if to_regex is not None:
                trc = re.compile(to_regex)
                for i in rec['to']:
                    if trc.match(i):
                        return True
                else:
                    return False
        else:
            if to_regex is not None:
                return False
        return True

    def queueMng(self,
                 mindate=None,
                 maxdate=None,
                 from_regex=None,
                 to_regex=None,
                 delete=False):
        '''Manage th Postfix mail queue - return dictionary
           with filtered or deleted messages'''
        mq = {}
        unparsed = []
        mp = subprocess.Popen([self.mailq],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
        rs = r'(\w+)[*!]?\s+(\d+)\s+(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+)\s+(%s)' % self.mail_reg
        fl_re = re.compile(rs)
        msg_re = re.compile(r'\s*\((.*)\)\s*')
        toaddr_re = re.compile(r'\s*(%s)\s*' % self.mail_reg)
        pmid = ''
        rec = {}
        while mp.poll() is None:
            for line in mp.stdout:
                if line[0] == '-':
                    continue
                elif line == '\n':
                    if self.isFilter(rec,
                                     mindate,
                                     maxdate,
                                     from_regex,
                                     to_regex):
                        if delete:
                            rec['deleted'] = self.dropMessage(pmid)
                        rec['time'] = rec['time'].isoformat(' ')
                        mq[pmid] = rec
                        rec = {}
                        pmid = ''
                    else:
                        rec = {}
                        pmid = ''
                        continue
                else:
                    fl_result = fl_re.match(line)
                    msg_result = msg_re.match(line)
                    toaddr_result = toaddr_re.match(line)
                    if fl_result:
                        pmid = fl_result.group(1)
                        rec['size'] = int(fl_result.group(2))
                        rec['time'] = datetime.datetime.strptime(fl_result.group(3),
                                                                 '%a %b %d %H:%M:%S')
                        n = datetime.datetime.now()
                        rec['time'] = rec['time'].replace(n.year)
                        if rec['time'] > n:
                            rec['time'].replace(n.year - 1)
                        rec['from'] = fl_result.group(4)
                    elif msg_result:
                        rec['message'] = msg_result.group(1)
                    elif toaddr_result:
                        if 'to' in rec.keys():
                            rec['to'].append(toaddr_result.group(1))
                        else:
                            rec['to'] = []
                            rec['to'].append(toaddr_result.group(1))
                    else:
                        unparsed.append(line)
        mq['unparsed'] = unparsed
        return mq


if __name__ == '__main__':  # main
    import argparse
    import json
    opt = argparse.ArgumentParser(description=__doc__,
                                  epilog='version: %s' % __version__)
    opt.add_argument('--mailqpath',
                     dest='mailqpath',
                     default='mailq',
                     help='Full path to mailq binary (default: %(default)s)')
    opt.add_argument('--pspath',
                     dest='pspath',
                     default='postsuper',
                     help=('Full path to postsuper binary '
                           '(default: %(default)s)'))
    opt.add_argument('--log-mask',
                     dest='log_mask',
                     default='mail.info*',
                     help='Mask for log file names (default: %(default)s)')
    opt.add_argument('--log-dir',
                     dest='log_dir',
                     default='/var/log',
                     help='Full path to log files dir (default: %(default)s)')
    opt.add_argument('--maxdate',
                     dest='maxdate',
                     default=None,
                     help=('Max date|time for filter messages in mail '
                           'queue (default: %(default)s)'))
    opt.add_argument('--mindate',
                     dest='mindate',
                     default=None,
                     help=('Min date|time for filter messages in mail '
                           'queue (default: %(default)s)'))
    opt.add_argument('--from-regex',
                     dest='from_regex',
                     default=None,
                     help=('RegEx for filter message by sender in '
                           'queue (default: %(default)s)'))
    opt.add_argument('--to-regex',
                     dest='to_regex',
                     default=None,
                     help=('RegEx for filter message by recipient in '
                           'queue (default: %(default)s)'))
    opt.add_argument('--regex',
                     dest='regex',
                     default=None,
                     action='append',
                     help=('RegEx for filter message by in '
                           'logs (default: %(default)s)'))
    opt.add_argument('-d', '--del',
                     dest='delete',
                     action='store_true',
                     help=('If used (True) - delete filtered messages '
                           'from queue (default: %(default)s)'))
    opt.add_argument('-s', '--save',
                     dest='save',
                     action='store_true',
                     help=('If used (True) - save result in file '
                           '%(prog)s_DATE_log.json (default: %(default)s)'))
    opt.add_argument('-j', '--json-only',
                     dest='json',
                     action='store_true',
                     help=('If used (True) - return to stdout only json '
                           ' (default: %(default)s)'))
    opt.add_argument('-q', '--quiet',
                     dest='quiet',
                     action='store_true',
                     help=('If used (True) - do not write result to '
                           'stdout (default: %(default)s)'))
    opt.add_argument('-f', '--fulllog',
                     dest='fulllog',
                     action='store_true',
                     help=('If used (True) - add to result information '
                           'from log files, used only where working with '
                           'mail queue (default: %(default)s)'))
    opt.add_argument('-z', '--gzip-json',
                     dest='gzipjson',
                     action='store_true',
                     help=('If used (True) - save result as gzipped json '
                           '(default: %(default)s)'))
    opt.add_argument('-o', '--one-proc',
                     dest='multiproc',
                     action='store_false',
                     help=('If used (False) - do not use multiprocessing'
                           '(default: %(default)s)'))
    opt.add_argument('-n', '--noindex',
                     dest='noindex',
                     action='store_true',
                     help=('If used (True) - no index log files, '
                           'use less memory (default: %(default)s)'))

    options = opt.parse_args()

    p = Postfix(mailq=options.mailqpath,
                postsuper=options.pspath,
                log_mask=options.log_mask,
                log_dir=options.log_dir,
                multiprocess=options.multiproc,
                noindex=options.noindex)
    if options.regex is not None:
        if not options.json:
            print('Parsing logs...')
        res = p.getPostfixMailLogs(options.regex)
    else:
        if not options.json:
            print('Parsing mail queue...')
        if options.mindate is not None:
            mindate = datetime.datetime.strptime(options.mindate,
                                                 '%Y-%m-%d %H:%M:%S')
        else:
            mindate = None
        if options.maxdate is not None:
            maxdate = datetime.datetime.strptime(options.maxdate,
                                                 '%Y-%m-%d %H:%M:%S')
        else:
            maxdate = None
        res = p.queueMng(mindate=mindate,
                         maxdate=maxdate,
                         from_regex=options.from_regex,
                         to_regex=options.to_regex,
                         delete=options.delete)
        if options.fulllog:
            if not options.json:
                print('Parsing logs...')
            idlist = list(res.keys())
            if 'unparsed' in idlist:
                idlist.remove('unparsed')
            logs = p.getPostfixMailLogsByID(idlist)
            for i in res.keys():
                if i in logs.keys():
                    res[i]['log'] = logs[i]

    if not options.quiet:
        print(json.dumps(res, indent=4, sort_keys=True))
    if options.save:
        fname = '%s_%s_log.json' % (sys.argv[0],
                                    datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        if options.gzipjson:
            fname = '%s.gz' % fname
            with gzip.open(fname, 'w') as f:
                f.write(json.dumps(res, indent=4, sort_keys=True).encode('utf-8'))
        else:
            with open(fname, encoding='utf-8', mode='w+') as f:
                json.dump(res, f, indent=4, sort_keys=True)
    if not options.json:
        print('\n Found %d records\n' % len(res))
