#!/usr/bin/env python3

from os.path import dirname, join, basename, normpath, expanduser
from platform import system
from textwrap import TextWrapper
from gi.repository import GLib


class Utils:

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
    def bn(name):
        """
        Normalize a file path then find the base name
        """
        return basename(normpath(name))

    @staticmethod
    def lnbr(text, char=70):
        """
        Given a string `text` and integer `char`, return a string with
        line breaks every `char` characters
        """
        t = TextWrapper(width=char, break_on_hyphens=False)
        return t.fill(text)
