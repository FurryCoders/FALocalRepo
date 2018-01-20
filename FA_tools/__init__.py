from .search import main as db_search
from .tools import tiers
from .repair import dberrors
from sys import platform
if platform not in ('win32', 'cygwin'):
    from .signal_handler_unix import sigint_block, sigint_ublock, sigint_check
else:
    from .signal_handler_windows import sigint_block, sigint_ublock, sigint_check
