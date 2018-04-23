from .tools import tiers, cookies_error

from sys import platform
if platform not in ('win32', 'cygwin'):
    from .signal_handler_unix import sigint_block, sigint_ublock, sigint_check, sigint_clear
else:
    from .signal_handler_windows import sigint_block, sigint_ublock, sigint_check, sigint_clear
