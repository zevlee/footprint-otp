#!/usr/bin/env python3

from os.path import dirname, join, basename, normpath, expanduser
from platform import system
from textwrap import TextWrapper
from gi.repository import GLib


class Fn:

    # config and data directories
    if system() == "Darwin":
        conf_dir = expanduser(
            "~/Library/Application Support/me.zevlee.FootprintOTP"
        )
        data_dir = conf_dir
    else:
        conf_dir = join(GLib.get_user_config_dir(), "Footprint OTP")
        data_dir = join(GLib.get_user_data_dir(), "Footprint OTP")
    # application version
    version = open(join(dirname(__file__), "..", "VERSION")).read()

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
