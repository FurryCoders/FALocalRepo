import sys
from datetime import datetime
import FA_var as favar

def log_trim(file=favar.log_file, lines=10000):
    with open(file, 'r') as f:
        log = f.readlines()

    if len(log) <= lines:
        return
    log = log[-lines:]

    with open(file, 'w') as f:
        for l in log: f.write(l)

def log_start(file=favar.log_file):
    with open(file, 'a')as log:
        log.write('*'*44+'\n')

class log:
    def normal(data='', file=favar.log_file):
        if '--log' not in sys.argv[1:] and '--logv' not in sys.argv[1:]:
            return
        with open(file, 'a') as log:
            log.write(f'{str(datetime.now())} | {data}\n')

    def verbose(data='', file=favar.log_file):
        if '--logv' not in sys.argv[1:]:
            return
        with open(file, 'a') as log:
            log.write(f'{str(datetime.now())} | {data}\n')
