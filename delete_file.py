#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

'''
delete_file.py: delete large file
https://github.com/eking-go/public-tools/
'''

__author__ = 'Nikolay Gatilov'
__copyright__ = 'Nikolay Gatilov'
__license__ = 'GPL'
# __version__ = '1.0.2017041112'
__maintainer__ = 'Nikolay Gatilov'
__email__ = 'eking.work@gmail.com'

SLEEP = 1
BLOCKSIZE = 1024*(1024**2) # 1b
DEBUG = False

if __name__ == "__main__":  # main
    os.nice(19)
    if DEBUG:
        print time.strftime("BEGIN: %Y-%m-%d %H:%M:%S")
    try:
        size = os.stat(sys.argv[1]).st_size
    except:
        print "Unable get the size of file! Use:\n %s filename" % sys.argv[0]
        sys.exit(1)
    while size > BLOCKSIZE:
        if DEBUG:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            print "WHILE: size=%d, delay=%d, blocksize=%d, datetime=%s" % (size,
                                                                           SLEEP,
                                                                           BLOCKSIZE,
                                                                           ts)
        f = open(sys.argv[1], 'ab')
        os.ftruncate(f.fileno(), size - BLOCKSIZE)
        os.fsync(f)
        size = os.fstat(f.fileno()).st_size
        f.close()
        time.sleep(SLEEP)
    os.unlink(sys.argv[1])
    if DEBUG:
        print time.strftime("EXIT: %Y-%m-%d %H:%M:%S\n")
