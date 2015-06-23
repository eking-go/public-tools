#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
for use in shell scripts - get/set params from file
'''

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '1.0.2015062318'
__maintainer__ = 'Nikolay Gatilov'
__email__ = 'eking.work@gmail.com'

import sys
import argparse
import logging
import paramiko
import socket
import ConfigParser
from datetime import datetime


version_fmt = '%Y.%m.%d %H:%M:%S'


def join_conf(conf1, conf2):
    '''
    function to merge the two configurations. Each section of the initial
    configurations (that will be merged) contains the configuration parameter
    "version". by joining configurations, parameters that present in only one
    of them is copied into the new, and of those parameters which are present
    in both configurations in the resulting configuration will be copied the
    one with the (relevant sections) 'version' newer.
    '''
    for i in conf1.sections():
        if conf2.has_section(i):
            if conf1.has_option(i, 'version'):
                cnv = datetime.strptime(conf1.get(i, 'version'), version_fmt)
            else:
                cnv = datetime.min
            if conf2.has_option(i, 'version'):
                cv = datetime.strptime(conf2.get(i, 'version'), version_fmt)
            else:
                cv = datetime.min
            if cv >= cnv:
                for j in conf1.options(i):
                    if not conf2.has_option(i, j):
                        conf2.set(i, j)
            else:
                for j in conf1.options(i):
                    conf2.set(i, j)
        else:
            conf2.add_section(i)
            for j in conf1.options(i):
                conf2.set(i, j)
    return conf2

#===================================== MAIN ==================================
if __name__ == '__main__':  # main
    version_now = datetime.now().strftime(version_fmt)

    # create logger
    logger = logging.getLogger(sys.argv[0])
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    t = datetime.now().strftime('%Y.%m.%d')
    fh = logging.FileHandler('%s_%s.log' % (sys.argv[0], t))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    fmtr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmtr)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='set/get/del/list/sectlist')
    parser.add_argument('--file', help='local file name')
    parser.add_argument('--node', help='IP/fqdn of node to connect')
    parser.add_argument('--key', help='key file',
                                 default='~/.ssh/id_rsa')
    parser.add_argument('--port', help='ssh port', type=int, default=22)
    parser.add_argument('--usr', help='user for connect', default='user')
    parser.add_argument('--pwd', help='password for user or key',
                                 default='password')
    parser.add_argument('--nf', help='file name of config on node')
    parser.add_argument('--section', help='section name', default='main')
    parser.add_argument('--option', help='variable name')
    parser.add_argument('--value', help='value')
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config_node = ConfigParser.RawConfigParser()
    config.read([args.file])

    if args.node and args.pwd and args.nf:
        ip = socket.gethostbyname(args.node)
        hn = socket.gethostbyaddr(ip)[0]
        logger.debug('Connecting to node... %s - %s' % (hn, ip))
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(ip,
                  username=args.usr,
                  port=args.port,
                  password=args.pwd,
                  key_filename=args.key,
                  timeout=600)
        sftp = s.open_sftp()
        try:
            f = sftp.file(sftp.normalize(args.nf), 'r')
            config_node.readfp(f)
            f.close()
        except:
            pass

    config = join_conf(config_node, config)

    if args.action == 'set':
        if not config.has_section(args.section):
            config.add_section(args.section)
        version_now = datetime.now().strftime(version_fmt)
        if not args.option:
            config.set(args.section, 'option', args.value)
        config.set(args.section, args.option, args.value)
        config.set(args.section, 'version', version_now)
    elif args.action == 'get':
        if config.has_section(args.section):
            if config.has_option(args.section, args.option):
                print config.get(args.section, args.option)
    elif args.action == 'del' or args.action == 'delete':
        if config.has_section(args.section):
            if args.option and config.has_option(args.section, args.option):
                config.remove_option(args.section, args.option)
            else:
                config.remove_section(args.section)
    elif args.action == 'list':
        if args.section and config.has_section(args.section):
            print ' '.join(config.options(args.section))
    elif args.action == 'sectlist':
        print ' '.join(config.sections())

    fh = open(args.file, 'w')
    config.write(fh)
    fh.close()
    if args.node and args.pwd and args.nf:
        f = sftp.file(args.nf, 'w')
        config.write(f)
        f.close()
        sftp.close()
        s.close()
