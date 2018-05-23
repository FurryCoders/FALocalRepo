from datetime import datetime
import FA_var as favar

def log_trim(file=favar.log_file, lines=10000):
    with open(file, 'r') as log:
        file = log.readlines()

    if len(file) <= lines:
        return
    file = file[-lines:]

    with open(file, 'w') as log:
        for l in file: log.write(l)

def log_start(file=favar.log_file):
    with open(file, 'a')as log:
        log.write('*'*44+'\n')

def log(data='', file=favar.log_file):
    with open(file, 'a')as log:
        log.write(f'{str(datetime.now())} | {data}\n')
