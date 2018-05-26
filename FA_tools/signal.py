import signal
from SignalBlock import sigblock
from .log import log

def signal_handler(signum, frame):
    log.verbose('SIGNAL -> caught SIGINT')
    sigblock._pending += (signum,)
    print('\b\b  \b\b', end='', flush=True)

def sigint_block():
    log.normal('SIGNAL -> block sigint')
    sigblock.block(signal.SIGINT, handler=signal_handler)

def sigint_ublock():
    log.normal('SIGNAL -> unblock sigint')
    sigblock.unblock(signal.SIGINT)

def sigint_check():
    if sigblock.pending(signal.SIGINT):
        log.normal('SIGNAL -> check sigint:True')
        return True
    else:
        log.verbose('SIGNAL -> check sigint:False')
        return False

def sigint_clear():
    log.normal('SIGNAL -> clear pending singint')
    sigblock.clear()
