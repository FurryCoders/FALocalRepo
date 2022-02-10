try:
    from supports_color import supportsColor

    supports_truecolor: bool = getattr(supportsColor.stdout, "has16m", False)
except TypeError:
    supports_truecolor: bool = False

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

_ansi_rgb: dict[str, tuple[int, int, int]] = {
    "black": (0, 0, 0),
    "red": (170, 0, 0),
    "green": (0, 170, 0),
    "yellow": (170, 170, 0),
    "blue": (0, 0, 170),
    "magenta": (170, 0, 170),
    "cyan": (0, 170, 170),
    "white": (170, 170, 170),
    "bright_black": (85, 85, 85),
    "bright_red": (255, 85, 85),
    "bright_green": (85, 255, 85),
    "bright_yellow": (255, 255, 85),
    "bright_blue": (85, 85, 255),
    "bright_magenta": (255, 85, 255),
    "bright_cyan": (85, 255, 255),
    "bright_white": (255, 255, 255),
}

# noinspection SpellCheckingInspection
css_colors: dict[str, str] = {
    "aliceblue": "#F0F8FF", "antiquewhite": "#FAEBD7", "aqua": "#00FFFF", "aquamarine": "#7FFFD4", "azure": "#F0FFFF",
    "beige": "#F5F5DC", "bisque": "#FFE4C4", "black": "#000000", "blanchedalmond": "#FFEBCD", "blue": "#0000FF",
    "blueviolet": "#8A2BE2", "brown": "#A52A2A", "burlywood": "#DEB887", "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00", "chocolate": "#D2691E", "coral": "#FF7F50", "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC", "crimson": "#DC143C", "cyan": "#00FFFF", "darkblue": "#00008B", "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B", "darkgray": "#A9A9A9", "darkgrey": "#A9A9A9", "darkgreen": "#006400",
    "darkkhaki": "#BDB76B", "darkmagenta": "#8B008B", "darkolivegreen": "#556B2F", "darkorange": "#FF8C00",
    "darkorchid": "#9932CC", "darkred": "#8B0000", "darksalmon": "#E9967A", "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B", "darkslategray": "#2F4F4F", "darkslategrey": "#2F4F4F", "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3", "deeppink": "#FF1493", "deepskyblue": "#00BFFF", "dimgray": "#696969",
    "dimgrey": "#696969", "dodgerblue": "#1E90FF", "firebrick": "#B22222", "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22", "fuchsia": "#FF00FF", "gainsboro": "#DCDCDC", "ghostwhite": "#F8F8FF", "gold": "#FFD700",
    "goldenrod": "#DAA520", "gray": "#808080", "grey": "#808080", "green": "#008000", "greenyellow": "#ADFF2F",
    "honeydew": "#F0FFF0", "hotpink": "#FF69B4", "indianred": "#CD5C5C", "indigo": "#4B0082", "ivory": "#FFFFF0",
    "khaki": "#F0E68C", "lavender": "#E6E6FA", "lavenderblush": "#FFF0F5", "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD", "lightblue": "#ADD8E6", "lightcoral": "#F08080", "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2", "lightgray": "#D3D3D3", "lightgrey": "#D3D3D3", "lightgreen": "#90EE90",
    "lightpink": "#FFB6C1", "lightsalmon": "#FFA07A", "lightseagreen": "#20B2AA", "lightskyblue": "#87CEFA",
    "lightslategray": "#778899", "lightslategrey": "#778899", "lightsteelblue": "#B0C4DE", "lightyellow": "#FFFFE0",
    "lime": "#00FF00", "limegreen": "#32CD32", "linen": "#FAF0E6", "magenta": "#FF00FF", "maroon": "#800000",
    "mediumaquamarine": "#66CDAA", "mediumblue": "#0000CD", "mediumorchid": "#BA55D3", "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371", "mediumslateblue": "#7B68EE", "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC", "mediumvioletred": "#C71585", "midnightblue": "#191970", "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1", "moccasin": "#FFE4B5", "navajowhite": "#FFDEAD", "navy": "#000080", "oldlace": "#FDF5E6",
    "olive": "#808000", "olivedrab": "#6B8E23", "orange": "#FFA500", "orangered": "#FF4500", "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA", "palegreen": "#98FB98", "paleturquoise": "#AFEEEE", "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5", "peachpuff": "#FFDAB9", "peru": "#CD853F", "pink": "#FFC0CB", "plum": "#DDA0DD",
    "powderblue": "#B0E0E6", "purple": "#800080", "rebeccapurple": "#663399", "red": "#FF0000", "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1", "saddlebrown": "#8B4513", "salmon": "#FA8072", "sandybrown": "#F4A460",
    "seagreen": "#2E8B57", "seashell": "#FFF5EE", "sienna": "#A0522D", "silver": "#C0C0C0", "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD", "slategray": "#708090", "slategrey": "#708090", "snow": "#FFFAFA", "springgreen": "#00FF7F",
    "steelblue": "#4682B4", "tan": "#D2B48C", "teal": "#008080", "thistle": "#D8BFD8", "tomato": "#FF6347",
    "turquoise": "#40E0D0", "violet": "#EE82EE", "wheat": "#F5DEB3", "white": "#FFFFFF", "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00", "yellowgreen": "#9ACD32"
}


def rgb_to_ansi_8bit(rgb: tuple[int, int, int]) -> str:
    return colors_dict[sorted(_ansi_rgb.items(), key=lambda c: sum(map(abs, (a - b for a, b in zip(c[1], rgb)))))[0][0]]


def hex_to_ansi(color_hex: str, *, truecolor: bool = True) -> str:
    color_hex = color_hex.removeprefix("#")
    rgb: tuple[int, int, int] = int(color_hex[0:2], base=16), int(color_hex[2:4], base=16), int(color_hex[4:6], base=16)
    return "\x1b[38;2;{};{};{}m".format(*rgb) if truecolor else rgb_to_ansi_8bit(rgb)
