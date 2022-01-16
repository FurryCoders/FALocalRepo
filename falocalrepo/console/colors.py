reset: str = "\x1b[0m"

black: str = "\x1b[30m"
red: str = "\x1b[31m"
green: str = "\x1b[32m"
yellow: str = "\x1b[33m"
blue: str = "\x1b[34m"
magenta: str = "\x1b[35m"
cyan: str = "\x1b[36m"
white: str = "\x1b[37m"
bright_black: str = "\x1b[90m"
bright_red: str = "\x1b[91m"
bright_green: str = "\x1b[92m"
bright_yellow: str = "\x1b[93m"
bright_blue: str = "\x1b[94m"
bright_magenta: str = "\x1b[95m"
bright_cyan: str = "\x1b[96m"
bright_white: str = "\x1b[97m"

bold: str = "\x1b[1m"
dim: str = "\x1b[2m"
underline: str = "\x1b[4m"
overline: str = "\x1b[53m"
italic: str = "\x1b[3m"
blink: str = "\x1b[5m"
reverse: str = "\x1b[7m"
strikethrough: str = "\x1b[9m"

colors_dict: dict[str, str] = {
    "reset": reset,
    "black": black,
    "red": red,
    "green": green,
    "yellow": yellow,
    "blue": blue,
    "magenta": magenta,
    "cyan": cyan,
    "white": white,
    "bright_black": bright_black,
    "bright_red": bright_red,
    "bright_green": bright_green,
    "bright_yellow": bright_yellow,
    "bright_blue": bright_blue,
    "bright_magenta": bright_magenta,
    "bright_cyan": bright_cyan,
    "bright_white": bright_white,
    "bold": bold,
    "dim": dim,
    "underline": underline,
    "overline": overline,
    "italic": italic,
    "blink": blink,
    "reverse": reverse,
    "strikethrough": strikethrough,
}
