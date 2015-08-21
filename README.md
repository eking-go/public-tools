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
