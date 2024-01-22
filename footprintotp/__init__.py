from os.path import dirname, join, basename, normpath, expanduser
from platform import system
from textwrap import TextWrapper
from json import loads, dumps
from gi.repository import GLib

# Application version
__version__ = "1.0.0"
# Application name
__appname__ = "Footprint OTP"
# Application ID
__id__ = "me.zevlee.FootprintOTP"
# Application directory
__appdir__ = dirname(dirname(__file__))
# Config and data directories
if system() == "Darwin":
    __conf__ = join(expanduser("~/Library/Application Support"), __id__)
    __data__ = __conf__
else:
    __conf__ = join(GLib.get_user_config_dir(), __appname__)
    __data__ = join(GLib.get_user_data_dir(), __appname__)
# Default settings
DEFAULT = {
    "dflt": expanduser("~"),
    "keys": join(__data__, "keys"),
    "save": "",
    "encf": False,
    "appr": True,
    "dbug": False
}


def bn(filename):
    """
    Normalize a file path then find the base filename

    :param filename: Filename
    :type filename: str
    :return: Base filename
    :rtype: str
    """
    return basename(normpath(filename))


def lnbr(text, char=70):
    """
    Given a string `text` and integer `char`, return a string with
    line breaks every `char` characters
    
    :param text: Text
    :type text: str
    :param char: Number of characters
    :type char: int
    :return: Text with line breaks
    :rtype: str
    """
    t = TextWrapper(width=char, break_on_hyphens=False)
    return t.fill(text)


def _read_config(filename):
    """
    Given a filename `filename`, return the configuration dictionary or
    the default configuration if `filename` is not found
    
    :param filename: Filename
    :type filename: str
    :return: Configuration dictionary
    :rtype: dict
    """
    try:
        config = loads(open(join(__conf__, filename), "r").read())
    except FileNotFoundError:
        config = DEFAULT
    return config


def validate_config(filename):
    """
    Given a filename `filename`, replace the file with filename `default`
    if it is not valid
    
    :param filename: Config filename
    :type filename: str
    :param default: Default filename
    :type default: str
    """
    overwrite = False
    config = _read_config(filename)
    # Remove invalid keys
    for key in [k for k in config.keys() if k not in DEFAULT.keys()]:
        config.pop(key)
        overwrite = True
    # Add missing keys
    for key in [k for k in DEFAULT.keys() if k not in config.keys()]:
        config[key] = DEFAULT[key]
        overwrite = True
    # Validate config options
    for k in ["encf", "appr", "dbug"]:
        if not isinstance(config[k], int):
            config[k] = DEFAULT[k]
            overwrite = True
    # Overwrite filename if there is an error
    if overwrite:
        with open(join(__conf__, filename), "w") as c:
            c.write(dumps(config))
            c.close()
