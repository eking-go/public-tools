# public-tools
This is independent tools for different purposes, not a single project


## check_raid_temp.py
nagios check Adaptec raid temperature plugin
```
$ ./check_raid_temp.py --help
usage: check_raid_temp.py [-h] [--wc WC] [--cc CC] [--wf WF] [--cf CF]

nagios check Adaptec raid temperature plugin Last version: https://github.com
/eking-go/public-tools

optional arguments:
  -h, --help  show this help message and exit
  --wc WC     Warning Celsius
  --cc CC     Critical Celsius
  --wf WF     Warning Fahrenheit
  --cf CF     Critical Fahrenheit

```

## params_s.py
for use in shell scripts - get/set params from file
```
$ ./params_s.py --help
usage: params_s.py [-h] [--file FILE] [--node NODE] [--key KEY] [--port PORT]
                   [--usr USR] [--pwd PWD] [--nf NF] [--section SECTION]
                   [--option OPTION] [--value VALUE]
                   action

positional arguments:
  action             set/get/del/list/sectlist

optional arguments:
  -h, --help         show this help message and exit
  --file FILE        local file name
  --node NODE        IP/fqdn of node to connect
  --key KEY          key file
  --port PORT        ssh port
  --usr USR          user for connect
  --pwd PWD          password for user or key
  --nf NF            file name of config on node
  --section SECTION  section name
  --option OPTION    variable name
  --value VALUE      value
```


## pre-commit
pre-commit git hook for check `__version__` in python scripts.
The version format: `__version__ = 'major.minor.datetime'`
datetime format (only digits, without ay non-digit characters) defined by
global variables of this script - `VERSION_FMT`

## dmesg.py 
dmesg with human-readable timestamps
I wrote this code just for fun and then found a similar tool:
https://gist.github.com/saghul/542780
but once wrote - let remains ;)

## remotearch.py

Utility to create a backup (recursive), a local directory on a remote
 server using ssh or ftp protocols. The archive file is created 
directly on a remote server without creating a local copy. 
Supported archives formats tar/tar.gz/tar.bz2 

In the local system should have the following python modules - `ftputil` and `paramiko`


```
$ ./remotearch.py
usage: remotearch.py [-h] [--lpath LPATH] [--node NODE] [--key KEY]
                     [--port PORT] [--usr USR] [--pwd PWD]
                     [--rarchive RARCHIVE] [--archtype ARCHTYPE]
                     [--proto PROTO]

archive local dir to remote FTP or SSH server. Last version:
https://github.com/eking-go/public-tools

optional arguments:
  -h, --help           show this help message and exit
  --lpath LPATH        local path to recursive archiving
  --node NODE          IP/fqdn of node to connect
  --key KEY            key file (for ssh)
  --port PORT          ssh/ftp port
  --usr USR            user for connect
  --pwd PWD            password for user or key
  --rarchive RARCHIVE  full file name of archive on remote node
  --archtype ARCHTYPE  type of archive: tar/tbz/tgz
  --proto PROTO        connection protocol - ftp/ssh
```


## postmgr.py

```
usage: postmgr.py [-h] [--mailqpath MAILQPATH] [--pspath PSPATH]
                  [--log-mask LOG_MASK] [--log-dir LOG_DIR]
                  [--maxdate MAXDATE] [--mindate MINDATE]
                  [--from-regex FROM_REGEX] [--to-regex TO_REGEX]
                  [--regex REGEX] [-d] [-s] [-j] [-q] [-f] [-z] [-o] [-n]

Manage Postfix queue and parse logs. If defined option --regex (and it not
Null) - script is parse logs, otherwise it working with mail queue. Date and
time format - %Y-%m-%d %H:%M:%S (ISO format)

optional arguments:
  -h, --help            show this help message and exit
  --mailqpath MAILQPATH
                        Full path to mailq binary (default: mailq)
  --pspath PSPATH       Full path to postsuper binary (default: postsuper)
  --log-mask LOG_MASK   Mask for log file names (default: mail.info*)
  --log-dir LOG_DIR     Full path to log files dir (default: /var/log)
  --maxdate MAXDATE     Max date|time for filter messages in mail queue
                        (default: None)
  --mindate MINDATE     Min date|time for filter messages in mail queue
                        (default: None)
  --from-regex FROM_REGEX
                        RegEx for filter message by sender in queue (default:
                        None)
  --to-regex TO_REGEX   RegEx for filter message by recipient in queue
                        (default: None)
  --regex REGEX         RegEx for filter message by in logs (default: None)
  -d, --del             If used (True) - delete filtered messages from queue
                        (default: False)
  -s, --save            If used (True) - save result in file
                        postmgr.py_DATE_log.json (default: False)
  -j, --json-only       If used (True) - return to stdout only json (default:
                        False)
  -q, --quiet           If used (True) - do not write result to stdout
                        (default: False)
  -f, --fulllog         If used (True) - add to result information from log
                        files, used only where working with mail queue
                        (default: False)
  -z, --gzip-json       If used (True) - save result as gzipped json (default:
                        False)
  -o, --one-proc        If used (False) - do not use multiprocessing(default:
                        True)
  -n, --noindex         If used (True) - no index log files, use less memory
                        (default: False)

version: 1.0.2017032412
```

## check_cassandra.py

```
usage: check_cassandra.py [-h] [--nodetool NODETOOL] [--host HOST]
                          [--port PORT] [--user USER] [--password PASSWORD]
                          [--hcc HCC] [--without_gossip] [--without_thrift]
                          [--without_native] [--fast_check]
                          [--coordinator_percentile COORDINATOR_PERCENTILE]
                          [--coordinator_RLW COORDINATOR_RLW]
                          [--coordinator_RLC COORDINATOR_RLC]
                          [--coordinator_WLW COORDINATOR_WLW]
                          [--coordinator_WLC COORDINATOR_WLC]
                          [--keyspace KEYSPACE]
                          [--ks_read_latency_w KS_READ_LATENCY_W]
                          [--ks_read_latency_c KS_READ_LATENCY_C]
                          [--ks_write_latency_w KS_WRITE_LATENCY_W]
                          [--ks_write_latency_c KS_WRITE_LATENCY_C]

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

optional arguments:
  -h, --help            show this help message and exit
  --nodetool NODETOOL   Full path to nodetool binary (default: nodetool)
  --host HOST           Host to connect (default: None - not use argument with
                        nodetool)
  --port PORT           Port to connect (default: None - not use argument with
                        nodetool)
  --user USER           Cassandra user to connect (default: None - not use
                        argument with nodetool)
  --password PASSWORD   Cassandra password to connect (default: None - not use
                        argument with nodetool)
  --hcc HCC             0..1 - critical % using HEAP (default: 1)
  --without_gossip      If used (True) - disabled gossip is not critical
                        (default: False)
  --without_thrift      If used (True) - disabled thrift is not critical
                        (default: False)
  --without_native      If used (True) - disabled native protocol is not
                        critical (default: False)
  --fast_check          If used (False) - do not check all - exit and return
                        the status as soon as the [W/C/U] value is received
                        (default: True)
  --coordinator_percentile COORDINATOR_PERCENTILE
                        coordinator percentile, for checking inter node
                        communication latency, see nodetool proxyhistograms
                        (default: 99%)
  --coordinator_RLW COORDINATOR_RLW
                        Inter-node communication read latency (from
                        coordinator, micros) WARNING value, None - Does not
                        cause a change in state (default: None)
  --coordinator_RLC COORDINATOR_RLC
                        Inter-node communication read latency (from
                        coordinator, micros) CRITICAL value, None - Does not
                        cause a change in state (default: None)
  --coordinator_WLW COORDINATOR_WLW
                        Inter-node communication write latency (from
                        coordinator, micros) WARNING value, None - Does not
                        cause a change in state (default: None)
  --coordinator_WLC COORDINATOR_WLC
                        Inter-node communication write latency (from
                        coordinator, micros) CRITICAL value, None - Does not
                        cause a change in state (default: None)
  --keyspace KEYSPACE   Keyspace for which to check read/write latency, see
                        nodetool tablestats. ALL - check all keyspaces
                        (default: None)
  --ks_read_latency_w KS_READ_LATENCY_W
                        Keyspace read latency WARNING value None - Does not
                        cause a change in state (default: None)
  --ks_read_latency_c KS_READ_LATENCY_C
                        Keyspace read latency CRITICAL value None - Does not
                        cause a change in state (default: None)
  --ks_write_latency_w KS_WRITE_LATENCY_W
                        Keyspace write latency WARNING value None - Does not
                        cause a change in state (default: None)
  --ks_write_latency_c KS_WRITE_LATENCY_C
                        Keyspace write latency CRITICAL value None - Does not
                        cause a change in state (default: None)

version: 1.0.2017033011
```

## xml_to_dict_parser.py - convert XML to dict


use only xml.parsers.expat - minimal dependenses, only for standard library.
For using with small utilites.

Example:
```
$ ./xml_to_dict_parser.py 
Example XML:

    <messages>
       <note id="501">
         <to>Tove</to>
         <from>Jani</from>
         <heading>Reminder</heading>
         <body>Don't forget me this weekend!</body>
       </note>
       <note id="502">
         <to>Jani</to>
         <from>Tove</from>
         <heading>Re: Reminder</heading>
         <body>I will not</body>
       </note>
    </messages>
    

Result with simplify:
{
    "subs": {
        "messages": {
            "note": {
                "attr": {
                    "id": "502"
                },
                "subs": {
                    "body": "I will not",
                    "from": "Tove",
                    "heading": "Re: Reminder",
                    "to": "Jani"
                }
            }
        }
    }
}


Result and without simplify:
{
    "subs": {
        "messages": {
            "subs": {
                "note": {
                    "attr": {
                        "id": "502"
                    },
                    "subs": {
                        "body": {
                            "data": "I will not"
                        },
                        "from": {
                            "data": "Tove"
                        },
                        "heading": {
                            "data": "Re: Reminder"
                        },
                        "to": {
                            "data": "Jani"
                        }
                    }
                }
            }
        }
    }
}

```
