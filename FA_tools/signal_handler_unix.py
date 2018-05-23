import signal
from .log import log

def sigint_block(logb=True):
    if logb: log.normal('SIGNAL -> sigint block')
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT})

def sigint_ublock(logb=True):
    if logb: log.normal('SIGNAL -> sigint unblock')
    signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT})

def sigint_check():
    if signal.SIGINT in signal.sigpending():
        log.normal('SIGNAL -> sigint check:True')
        return True
    else:
        return False

def sigint_clear():
    log.normal('SIGNAL -> sigint clear')
    while True:
        try:
            sigint_ublock(logb=False)
            break
        except:
            pass
    sigint_block(logb=False)
