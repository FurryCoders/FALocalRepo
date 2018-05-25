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
    _normal = '--log' in sys.argv[1:] or '--logv' in sys.argv[1:]
    _verbose = '--logv' in sys.argv[1:]
    _file = favar.log_file

    @classmethod
    def normal(cls, data=''):
        if not cls._normal:
            return
        with open(cls._file, 'a') as log:
            log.write(f'{str(datetime.now())} | N | {data}\n')

    @classmethod
    def verbose(cls, data=''):
        if not cls._verbose:
            return
        with open(cls._file, 'a') as log:
            log.write(f'{str(datetime.now())} | V | {data}\n')

    @classmethod
    def warning(cls, data=''):
        with open(cls._file, 'a') as log:
            log.write(f'{str(datetime.now())} | W | {data}\n')
