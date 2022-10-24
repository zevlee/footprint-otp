#!/usr/bin/env python3

from os.path import dirname, join, basename, normpath, expanduser
from platform import system
from textwrap import TextWrapper
from json import loads, dumps
from gi.repository import GLib


class Utils:
    """
    Utilities
    """
    # Application name
    NAME = "Footprint OTP"

    # Application ID
    ID = "me.zevlee.FootprintOTP"

    # Application directory
    APP_DIR = dirname(dirname(__file__))

    # Application version
    VERSION = open(join(APP_DIR, "VERSION")).read()

    # Config and data directories
    if system() == "Darwin":
        CONFIG_DIR = join(expanduser("~/Library/Application Support"), ID)
        DATA_DIR = CONFIG_DIR
    else:
        CONFIG_DIR = join(GLib.get_user_config_dir(), NAME)
        DATA_DIR = join(GLib.get_user_data_dir(), NAME)

    DEFAULT = {
        "dflt": expanduser("~"),
        "keys": join(DATA_DIR, "keys"),
        "save": "",
        "appr": True,
        "dbug": False
    }

    @staticmethod
    def bn(filename):
        """
        Normalize a file path then find the base filename

        :param filename: Filename
        :type filename: str
        :return: Base filename
        :rtype: str
        """
        return basename(normpath(filename))

    @staticmethod
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
    
    @staticmethod
    def read_config(filename):
        """
        Given a filename `filename`, return the configuration dictionary or
        the default configuration if `filename` is not found
        
        :param filename: Filename
        :type filename: str
        :return: Configuration dictionary
        :rtype: dict
        """
        try:
            config = loads(open(join(Utils.CONFIG_DIR, filename), "r").read())
        except FileNotFoundError:
            config = Utils.DEFAULT
        return config
    
    @staticmethod
    def validate_config(filename, default="RESET"):
        """
        Given a filename `filename`, replace the file with filename `default`
        if it is not valid
        
        :param filename: Default filename
        :type filename: str
        :param filename: Config filename
        :type filename: str
        """
        overwrite = False
        default_config = Utils.read_config(default)
        config = Utils.read_config(filename)
        # Remove invalid keys
        for key in [k for k in config.keys() if k not in Utils.DEFAULT.keys()]:
            config.pop(key)
            overwrite = True
        # Add missing keys
        for key in [k for k in Utils.DEFAULT.keys() if k not in config.keys()]:
            config[key] = default_config[key]
            overwrite = True
        # Validate config options
        for k in ["appr", "dbug"]:
            if not isinstance(config[k], int):
                config[k] = default_config[k]
                overwrite = True
        # Overwrite filename if there is an error
        if overwrite:
            with open(join(Utils.CONFIG_DIR, filename), "w") as c:
                c.write(dumps(config))
                c.close()
