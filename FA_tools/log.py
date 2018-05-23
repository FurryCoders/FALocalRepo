from datetime import datetime
import FA_var as favar

def log_trim(file=favar.log_file, lines=10000):
    with open(file, 'r') as log: file = log.readlines()
    file = file[-lines:]
    with open(file, 'w') as log: log.writelines(file)

def log(data='', file=favar.log_file):
    with open(file, 'a')as log:
        log.write(f'{str(datetime.datetime.now())} | {data}\n')
