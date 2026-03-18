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
        _safe_print("\t\t.▄▄ · ▄ •▄ ▪   ▄▄▄·▄▄▄▄▄▄▄▄   ▄▄▄·  ▄▄· ▄▄▄ .▄▄▄  ")
        _safe_print("\t\t▐█ ▀. █▌▄▌▪██ ▐█ ▄█•██  ▀▄ █·▐█ ▀█ ▐█ ▌▪▀▄.▀·▀▄ █·")
        _safe_print("\t\t▄▀▀▀█▄▐▀▀▄·▐█· ██▀· ▐█.▪▐▀▀▄ ▄█▀▀█ ██ ▄▄▐▀▀▪▄▐▀▀▄ ")
        _safe_print("\t\t▐█▄▪▐█▐█.█▌▐█▌▐█▪·• ▐█▌·▐█•█▌▐█ ▪▐▌▐███▌▐█▄▄▌▐█•█▌")
        _safe_print(
            ("\t\t       {},.-~*´¨¯¨`*·~-.¸{}-({}by{})-{},.-~*´¨¯¨`*·~-.¸{} \n").format(
                bc.CRED, bc.CYLW, bc.CCYN, bc.CYLW, bc.CRED, bc.CEND))
        _safe_print(
            ("\t\t\t      {}skiptr4cer {}reloaded{}").format(
                bc.CBLU, bc.CRED, bc.CEND))
        _safe_print(
            ("\t\t\t      {}  https://github.com/84KaliPleXon3/skiptracer {}\n").format(
                bc.CYLW, bc.CEND))
