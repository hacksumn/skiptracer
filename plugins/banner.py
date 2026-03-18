# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from plugins.colors import BodyColors as bc


def _safe_print(text):
    """Print text, falling back to ASCII replacement on encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


class Logo:

    def __init__(self):
        pass

    def banner(self):
        _safe_print("")
        _safe_print(bc.CCYN + "    ____                    _          ____            " + bc.CEND)
        _safe_print(bc.CCYN + "   / __ \\__  ______  ____  (_)___     / __ \\____  _____" + bc.CEND)
        _safe_print(bc.CCYN + "  / /_/ / / / / __ \\/ __ \\/ / __ \\   / / / / __ \\/ ___/" + bc.CEND)
        _safe_print(bc.CCYN + " / _, _/ /_/ / / / / / / / / / / /  / /_/ / /_/ (__  ) " + bc.CEND)
        _safe_print(bc.CCYN + "/_/ |_|\\__,_/_/ /_/_/ /_/_/_/ /_/   \\____/ .___/____/  " + bc.CEND)
        _safe_print(bc.CCYN + "                                         /_/            " + bc.CEND)
        _safe_print("")
        _safe_print(
            "\t   {},.-~*`*·~-.¸{}  {}Runnin' Ops{}  {},.-~*`*·~-.¸{}".format(
                bc.CRED, bc.CEND, bc.CCYN, bc.CEND, bc.CRED, bc.CEND))
        _safe_print(
            "\t\t   {}OSINT Framework  |  by {}Jake Palmer{}".format(
                bc.CYLW, bc.CGRN, bc.CEND))
        _safe_print(
            "\t\t   {}https://github.com/hacksumn/skiptracer{}\n".format(
                bc.CBLU, bc.CEND))
