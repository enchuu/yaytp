import time
import string
from unicodedata import east_asian_width


def get_real_width(str):
    """Gets real width of a string accounting for double width characters."""

    real_width = 0
    for char in str:
        real_width += 2 if east_asian_width(char) == 'W' else 1
    return real_width


def fit_string_split(str, width):
    """Fits a string into a width, truncates if it is over and pads if it is under.
    Returns a tuple with the first entry being the fitted part and the second
    the rest of the string.
    """

    real_width = 0
    index = 0
    while (index < len(str)):
        double_width = east_asian_width(str[index]) == 'W'
        real_width += 2 if double_width else 1
        if (real_width > width):
            padding = 0
            while (str[index] in string.ascii_letters + string.digits  and east_asian_width(str[index]) != 'W'):
                index -= 1
                padding += 1 
            if (double_width and real_width - width == 1):
                return (str[0:index] + ' ' * (padding + 1), str[index + 1:])
            else:
                return (str[0:index] + ' ' * (padding) , str[index + 1:])
        index += 1
    return (str + ' ' * (width - real_width), '')


def fit_string(str, width):
    """Does the same thing as fit_string_split but does not return the second part."""

    return fit_string_split(str, width)[0]


def quick_fit_string(str, width, left_align = True, pad = ' '):
    """Fits a string into a width. Does not check for double width characters."""
    if (len(str) > width):
        return str[0:width]
    else:
        padding = pad * (width - len(str))
        if (left_align):
            return str + padding
        else:
            return padding + str


def trunc_int(num, len):
    """Truncates an int to a string of a certain length."""

    if (num < 10 ** len):
        return str(num)
    elif (num // 1000 < 10 ** (len - 1)):
        return str(num // 1000) + 'k'
    elif (num // 1000000 < 10 ** (len -1)):
        return str(num // 1000000) + 'm'
    else: 
        return str(num // 1000000000) + 'b'


def format_int(num, len):
    """Formats an into into a string of a certain length."""

    return quick_fit_string(trunc_int(num, len), len)
    

def format_time(secs):
    """Format a length of a video."""

    hms = time.strftime('%H:%M:%S', time.gmtime(secs))
    i = 0
    while (hms[i] in '0:' and i < 4):
        i += 1
    return hms[i:]


def center(items, width):
    """Centers a list of items putting an equal amount of spacing between each item."""

    cur_width = 0
    for item in items:
        cur_width += len(item)
    spacing = (width - cur_width) // (len(items) - 1)
    line = ''
    for item in items:
        line += item + ' ' * spacing
    line = line[0:len(line) - spacing]
    line = ' ' * ((width - len(line)) // 2) + line
    return line
