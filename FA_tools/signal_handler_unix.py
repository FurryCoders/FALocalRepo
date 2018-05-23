import signal
from .log import log

def sigint_block():
    log('SIGNAL -> sigint block')
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT})

def sigint_ublock():
    log('SIGNAL -> sigint unblock')
    signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT})

def sigint_check():
    if signal.SIGINT in signal.sigpending():
        log('SIGNAL -> sigint check:True')
        return True
    else:
        return False

def sigint_clear():
    log('SIGNAL -> sigint clear')
    while True:
        try:
            sigint_ublock()
            break
        except:
            pass
    sigint_block()
