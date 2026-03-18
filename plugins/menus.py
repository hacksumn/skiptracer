# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import print_function
from plugins.banner import Logo
from plugins.who_call_id import WhoCallIdGrabber
from plugins.advance_background_checks import AdvanceBackgroundGrabber
from plugins.myspace import MySpaceGrabber
from plugins.linkedin import LinkedInGrabber
from plugins.haveibeenpwned import HaveIBeenPwwnedGrabber
from plugins.plate import VinGrabber
from plugins.crt import SubDomainGrabber
from plugins.tinder import TinderGrabber
from plugins.colors import BodyColors as bc
from plugins.reporter import ReportGenerator
from plugins.username_check import UsernameChecker
from plugins.breach_check import BreachChecker
from plugins.github_lookup import GitHubLookup
import json
import os
import sys
import signal

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


def signal_handler(sig, frame):
    print("")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class menus():

    def helpmenu(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            Logo().banner()
            print("\t[INFORMATION]::")
            print("""
This application is designed to query and parse 3rd party services in an automated fashion
to increase productivity while conducting a background investigation.

\tEmail:      Investigate with a known email address
\tUsername:   Investigate with a known screen name / alias
\tPhone:      Investigate with a known US phone number
\tDomain:     Enumerate subdomains via Certificate Transparency logs
\tPlate:      Decode a license plate / VIN via NHTSA free API

:: EMAIL ::
  Format: username@domain.tld
  Modules:
    - Breach Check    : LeakCheck.io + XposedOrNot (no API key needed)
    - HaveIBeenPwned  : HIBP v3 API (requires free API key)
    - GitHub Search   : Find GitHub accounts linked to email
    - LinkedIn        : Requires LinkedIn credentials
    - Myspace         : Myspace account lookup

:: USERNAME ::
  Format: Ac1dBurn
  Modules:
    - Username Check  : Checks 35+ platforms concurrently
    - Tinder          : Tinder profile lookup
    - GitHub          : Direct GitHub user lookup

:: PHONE ::
  Format: 4075551234
  Modules:
    - WhoCalld        : Reverse phone lookup

:: DOMAIN ::
  Format: example.com
  Modules:
    - crt.sh          : Subdomain enumeration via Certificate Transparency

:: PLATE ::
  Format: ABC1234  (then prompted for state)
  Modules:
    - NHTSA VIN Decode: Free government API — make, model, year, engine, etc.
""")
            input("\nPress ENTER to continue")
            self.intromenu()
        except Exception as e:
            print("Help failed: %s" % e)

    def intromenu(self):
        bi.search_string = None
        bi.lookup = None
        Logo().banner()
        print(" [{}!{}] {}Lookup menu:{}".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND))
        print('\t[{}1{}] {}Email{}      - {}Search by email address{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}Username{}   - {}Search by screen name / alias{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}Phone{}      - {}Search by telephone number{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}4{}] {}Domain{}     - {}Enumerate subdomains{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}5{}] {}Plate{}      - {}License plate / VIN decode{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}6{}] {}Help{}       - {}Usage and module details{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}88{}] {}Report{}    - {}Generate DOCX report from session data{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}99{}] {}Exit{}      - {}Quit{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        try:
            gselect = int(input("\n[{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.intromenu()
            return
        if gselect == 99:
            sys.exit(0)
        dispatch = {1: self.emailmenu, 2: self.snmenu, 3: self.phonemenu,
                    4: self.domainmenu, 5: self.platemenu, 6: self.helpmenu,
                    88: self.repgen}
        if gselect in dispatch:
            try:
                dispatch[gselect]()
            except Exception:
                pass
        self.intromenu()

    def repgen(self):
        try:
            ReportGenerator().newdoc()
            ReportGenerator().addtitle('SkipTracer Report')
            for header in bi.outdata.keys():
                ReportGenerator().addheader(str(header), 1)
                def sorttype(feed):
                    try:
                        feed = eval(str(json.dumps(feed)))
                    except Exception:
                        pass
                    try:
                        if isinstance(feed, dict):
                            for k in feed.keys():
                                ReportGenerator().addheader(str(k), 2)
                                sorttype(bi.outdata[header][k])
                        elif isinstance(feed, list):
                            for item in feed:
                                ReportGenerator().unorderedlist(str(item))
                        elif isinstance(feed, str):
                            ReportGenerator().unorderedlist(feed)
                    except Exception as e:
                        print("Key failed: %s" % e)
                sorttype(bi.outdata[header])
            ReportGenerator().savefile('./skiptracer.docx')
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+"Report saved: ./skiptracer.docx\n"+bc.CEND)
        except Exception as e:
            print("Report generation failed: %s" % e)

    # ─────────────────────────────── EMAIL ────────────────────────────────

    def emailmenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Email search menu{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}Run all email modules{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}Breach Check{}       - {}LeakCheck.io + XposedOrNot (free, no key){}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}HaveIBeenPwned{}     - {}HIBP v3 (requires API key){}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}4{}] {}GitHub Search{}      - {}Find GitHub accounts linked to email{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}5{}] {}Myspace{}            - {}Check for Myspace account{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}6{}] {}LinkedIn{}           - {}LinkedIn lookup (requires credentials){}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}7{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}8{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.emailmenu()
            return
        if gselect == 8:
            return
        if not bi.search_string or gselect == 7:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target email: {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 7:
                self.emailmenu()
                return
        bi.lookup = 'email'
        print()
        try:
            if gselect == 1:
                BreachChecker().get_info(bi.search_string)
                HaveIBeenPwwnedGrabber().get_info(bi.search_string)
                GitHubLookup().get_info_by_email(bi.search_string)
                MySpaceGrabber().get_info(bi.search_string)
                LinkedInGrabber().get_info(bi.search_string)
            elif gselect == 2:
                BreachChecker().get_info(bi.search_string)
            elif gselect == 3:
                HaveIBeenPwwnedGrabber().get_info(bi.search_string)
            elif gselect == 4:
                GitHubLookup().get_info_by_email(bi.search_string)
            elif gselect == 5:
                MySpaceGrabber().get_info(bi.search_string)
            elif gselect == 6:
                LinkedInGrabber().get_info(bi.search_string)
        except Exception:
            pass
        input("\nPress ENTER to continue")
        self.emailmenu()

    # ─────────────────────────────── USERNAME ────────────────────────────────

    def snmenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Username search menu{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}Run all username modules{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}Username Check{}     - {}Check 35+ platforms concurrently{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}GitHub{}             - {}Direct GitHub user lookup{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}4{}] {}Tinder{}             - {}Tinder profile lookup{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}5{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}6{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.snmenu()
            return
        if gselect == 6:
            return
        if not bi.search_string or gselect == 5:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target username: {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 5:
                self.snmenu()
                return
        bi.lookup = 'sn'
        print()
        try:
            if gselect == 1:
                UsernameChecker().get_info(bi.search_string)
                GitHubLookup().get_info(bi.search_string)
                TinderGrabber().get_info(bi.search_string)
            elif gselect == 2:
                UsernameChecker().get_info(bi.search_string)
            elif gselect == 3:
                GitHubLookup().get_info(bi.search_string)
            elif gselect == 4:
                TinderGrabber().get_info(bi.search_string)
        except Exception:
            pass
        input("\nPress ENTER to continue")
        self.snmenu()

    # ─────────────────────────────── PHONE ────────────────────────────────

    def phonemenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Phone search menu{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}Run all phone modules{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}WhoCalld{}           - {}Reverse phone lookup{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}4{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.phonemenu()
            return
        if gselect == 4:
            return
        if not bi.search_string or gselect == 3:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target phone (10 digits): {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 3:
                self.phonemenu()
                return
        bi.lookup = 'phone'
        print()
        try:
            if gselect in [1, 2]:
                WhoCallIdGrabber().get_info(bi.search_string)
        except Exception:
            pass
        input("\nPress ENTER to continue")
        self.phonemenu()

    # ─────────────────────────────── DOMAIN ────────────────────────────────

    def domainmenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Domain search menu{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}Run all domain modules{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}Subdomain (crt.sh){}  - {}Certificate Transparency subdomain enum{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}4{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.domainmenu()
            return
        if gselect == 4:
            return
        if not bi.search_string or gselect == 3:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target domain (e.g. example.com): {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 3:
                self.domainmenu()
                return
        bi.lookup = 'domain'
        print()
        try:
            if gselect in [1, 2]:
                SubDomainGrabber().get_info(bi.search_string)
        except Exception:
            pass
        input("\nPress ENTER to continue")
        self.domainmenu()

    # ─────────────────────────────── PLATE ────────────────────────────────

    def platemenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Plate / VIN lookup{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}Plate Lookup{}      - {}Plate + NHTSA VIN decode (free government API){}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}3{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.platemenu()
            return
        if gselect == 3:
            return
        if not bi.search_string or gselect == 2:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target plate number: {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 2:
                self.platemenu()
                return
        bi.lookup = 'plate'
        print()
        try:
            if gselect == 1:
                VinGrabber().get_info(bi.search_string)
        except Exception:
            pass
        input("\nPress ENTER to continue")
        self.platemenu()
