#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
archive local dir to remote FTP or SSH server.
Last version: https://github.com/eking-go/public-tools
'''

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
__version__ = '0.2.2016010222'
__maintainer__ = 'Nikolay Gatilov'

import sys
import os.path
import argparse
import paramiko
import tarfile
import ftplib
import ftputil
import ftputil.session
import socket


def sftp_mkdir_p(sftp, path):
    sftp.chdir('.')
    if path[-1] == '/':
        path = path[:-1]
    if path[0] == '/':
        path = path[1:]
        sftp.chdir('/')
    pl = path.split('/')
    for it in pl:
        try:
            sftp.chdir(it)
        except:
            try:
                sftp.mkdir(it)
                sftp.chdir(it)
            except:
                print 'Unable to create dir in ' % sftp.getcwd()

            
def archive(f, lpath, archtype):
    if archtype == 'tbz':
        tar = tarfile.open(mode='w|bz2', fileobj=f, bufsize=1024)
    elif archtype == 'tgz':
        tar = tarfile.open(mode='w|gz', fileobj=f, bufsize=1024)
    else:
        tar = tarfile.open(mode='w|', fileobj=f, bufsize=1024)
    print 'Recursive scan local path %s' % lpath
    filelist = []
    for i in lpath:
        if os.path.isdir(i):
            for root, dirs, files in os.walk(i):
                for name in files: filelist.append(os.path.join(root, name))
        else:
            filelist.append(i)
    nf = len(filelist)
    n = 1
    print 'Found %d files' % nf
    for name in filelist:
        print 'Adding (%d/%d) %s' % (n, nf, name)
        n = n + 1
        tar.add(name)
    tar.close()


# ===================================== MAIN =================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog='--lpath may be specified'
                                            ' more than once')
    parser.add_argument('--lpath', help='local path to recursive archiving',
                        action='append')
    parser.add_argument('--node', help='IP/fqdn of node to connect')
    parser.add_argument('--key', help='key file (for ssh)', default=None)
    parser.add_argument('--port', help='ssh/ftp port', type=int)
    parser.add_argument('--usr', help='user for connect',
                        default='anonymous@example.net')
    parser.add_argument('--pwd', help='password for user or key',
                        default='password')
    parser.add_argument('--rarchive',
                        help='full file name of archive on remote node')
    parser.add_argument('--archtype', help='type of archive: tar/tbz/tgz',
                        default='tbz')
    parser.add_argument('--proto', help='connection protocol - ftp/ssh',
                        default='ssh')
    args = parser.parse_args()
    
    if args.node and args.lpath and args.rarchive:
        ip = socket.gethostbyname(args.node)
        hn = socket.gethostbyaddr(ip)[0]
        aname = os.path.basename(args.rarchive)
        apath = os.path.dirname(args.rarchive)
        if not args.port:
            if args.proto == 'ssh':
                port = 22
            else:
                port = 21
        else:
            port = args.port
        print 'Connecting to node... %s - %s' % (hn, ip)
    else:
        parser.print_help()
        sys.exit()
    
    if args.proto == 'ssh':
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(ip,
                  username=args.usr,
                  port=port,
                  password=args.pwd,
                  key_filename=args.key,
                  timeout=600)
        sftp = s.open_sftp()
        try:
            sftp_mkdir_p(sftp, apath)
            f = sftp.file(aname, 'w')
            archive(f, args.lpath, args.archtype)
        except:
            print ('Error: unable open file %s in the directory '
                  '%s on the remote SSH server') % (aname, apath)
        sftp.close()
        s.close()
    else:
        my_session_factory = ftputil.session.session_factory(
                               base_class=ftplib.FTP,
                               port=port,
                               use_passive_mode=None,
                               debug_level=0)
        with ftputil.FTPHost(ip, args.usr, args.pwd,
                             session_factory=my_session_factory) as ftp_host:
            try:
                ftp_host.makedirs(apath)
                ftp_host.chdir(apath)
                f = ftp_host.open(aname, mode='wb')
                archive(f, args.lpath, args.archtype)
            except:
                print ('Error: unable open file %s in the directory'
                       '%s on the remote FTP server') % (aname, apath)
            ftp_host.close()
