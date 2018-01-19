from .search import search as db_search

from sys import platform
if platform not in ('win32', 'cygwin'):
    from .signal_handler_unix import sigint_block, sigint_ublock, sigint_check
else:
    from .signal_handler_windows import sigint_block, sigint_ublock, sigint_check
