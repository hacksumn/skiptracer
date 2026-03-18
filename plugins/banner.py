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
        _safe_print(bc.CCYN + "\t\t  _____ _    _       _                       " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t / ____| |  (_)     | |                      " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t| (___ | | ___ _ __ | |_ _ __ __ _  ___ ___  " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t \\___ \\| |/ / | '_ \\| __| '__/ _` |/ __/ _ \\ " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t ____) |   <| | |_) | |_| | | (_| | (_|  __/ " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t|_____/|_|\\_\\_| .__/ \\__|_|  \\__,_|\\___\\___| " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t              | |                            " + bc.CEND)
        _safe_print(bc.CCYN + "\t\t              |_|                            " + bc.CEND)
        _safe_print(
            ("\t\t       {},.-~*´¨¯¨`*·~-.¸{}-({}OSINT Framework{})-{},.-~*´¨¯¨`*·~-.¸{} \n").format(
                bc.CRED, bc.CYLW, bc.CCYN, bc.CYLW, bc.CRED, bc.CEND))
        _safe_print(
            ("\t\t\t      {}skiptracer {}modernized{}").format(
                bc.CBLU, bc.CRED, bc.CEND))
        _safe_print(
            ("\t\t\t      {}  https://github.com/hacksumn/skiptracer {}\n").format(
                bc.CYLW, bc.CEND))
