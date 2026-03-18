# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from __future__ import print_function
from plugins.menus import menus
from plugins.banner import Logo

import sys
import signal
import json

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

from plugins.colors import BodyColors as bc


def signal_handler(sig, frame):
    print("")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

bi.search_string = None
bi.lookup = None
bi.output = None
bi.outdata = dict()
bi.webproxy = None
bi.proxy = None
bi.debug = False

Logo().banner()

if __name__ == "__main__":
    try:
        menus().intromenu()
    except KeyboardInterrupt:
        print("")
        sys.exit(0)
    except Exception as failedmenu:
        print("Failed to launch menu: %s" % failedmenu)
        sys.exit(1)
