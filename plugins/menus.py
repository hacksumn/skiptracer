# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import print_function
from plugins.banner import Logo
from plugins.who_call_id import WhoCallIdGrabber
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
from plugins.dating_check import DatingChecker
from plugins.email_rep import EmailRepChecker
from plugins.gravatar import GravatarLookup
from plugins.ip_lookup import IPLookup
from plugins.whois_lookup import WhoisLookup
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
SkipTracer — passive OSINT reconnaissance toolkit.
All modules use free public APIs or public-facing web sources.

:: EMAIL ::  (format: user@domain.tld)
  - EmailRep.io      : Reputation, breach status, spam/blacklist, social profiles,
                       first/last seen, spoofability, deliverability [FREE, no key]
  - Breach Check     : LeakCheck.io + XposedOrNot dual breach lookup [FREE, no key]
  - HaveIBeenPwned   : HIBP v3 breach check [requires free API key]
  - Gravatar         : Email -> name, bio, location, linked accounts [FREE, no key]
  - GitHub Search    : Find GitHub accounts linked to an email [FREE, no key]
  - LinkedIn         : Profile lookup [requires LinkedIn credentials]

:: USERNAME :: (format: Ac1dBurn)
  - Username Check   : 35+ platforms concurrently (GitHub, Reddit, Instagram,
                       TikTok, Twitter, Twitch, Telegram, Steam, Spotify...) [FREE]
  - GitHub           : Full profile — repos, bio, followers, company [FREE, no key]
  - Tinder           : Tinder profile lookup [requires phone token]

:: PHONE :: (format: 4075551234)
  - WhoCalld         : Reverse phone — carrier, location, caller ID [FREE, no key]

:: DOMAIN / IP :: (format: example.com or 1.2.3.4)
  - WHOIS / RDAP     : Registrant, registrar, dates, nameservers [FREE, no key]
  - Subdomains (crt) : Certificate Transparency subdomain enum [FREE, no key]
  - IP Lookup        : Geolocation (country/city/ISP/ASN) + Shodan open ports,
                       CVEs, hostnames, tags [FREE, no key]

:: PLATE :: (format: ABC1234, then prompted for state)
  - NHTSA VIN Decode : Make, model, year, engine, fuel type [FREE gov API]

:: DATING :: (format: username)
  - Dating Check     : 38 platforms — OkCupid, POF, Hinge, Feeld, Badoo, Zoosk,
                       AFF, Ashley Madison, FetLife, Grindr, Scruff, Hornet, Reddit
                       and more. Tinder/Bumble/3Fun are mobile-only. [FREE, no key]
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
        print('\t[{}4{}] {}Domain/IP{}  - {}WHOIS, subdomains, IP geolocation + Shodan{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}5{}] {}Plate{}      - {}License plate / VIN decode{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}6{}] {}Dating{}     - {}Search 38 dating platforms by username{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}7{}] {}Help{}       - {}Usage and module details{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
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
                    4: self.domainmenu, 5: self.platemenu, 6: self.datingmenu,
                    7: self.helpmenu, 88: self.repgen}
        if gselect in dispatch:
            try:
                dispatch[gselect]()
            except Exception:
                pass
        self.intromenu()

    def repgen(self):
        try:
            ReportGenerator().newdoc()
            ReportGenerator().addtitle("Runnin' Ops Report")
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
            ReportGenerator().savefile('./runninops.docx')
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+"Report saved: ./runninops.docx\n"+bc.CEND)
        except Exception as e:
            print("Report generation failed: %s" % e)

    # ─────────────────────────────── EMAIL ────────────────────────────────

    def emailmenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Email search menu{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}Run all email modules{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}EmailRep{}           - {}Reputation, breach, social profiles, spam [free]{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}Breach Check{}       - {}LeakCheck.io + XposedOrNot [free, no key]{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}4{}] {}Gravatar{}           - {}Email -> name, bio, linked accounts [free]{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}5{}] {}GitHub Search{}      - {}Find GitHub accounts linked to email [free]{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}6{}] {}HaveIBeenPwned{}     - {}HIBP v3 (requires free API key){}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}7{}] {}LinkedIn{}           - {}LinkedIn lookup (requires credentials){}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}8{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}9{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.emailmenu()
            return
        if gselect == 9:
            return
        if not bi.search_string or gselect == 8:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target email: {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 8:
                self.emailmenu()
                return
        bi.lookup = 'email'
        print()
        try:
            if gselect == 1:
                EmailRepChecker().get_info(bi.search_string)
                BreachChecker().get_info(bi.search_string)
                GravatarLookup().get_info(bi.search_string)
                GitHubLookup().get_info_by_email(bi.search_string)
                HaveIBeenPwwnedGrabber().get_info(bi.search_string)
                LinkedInGrabber().get_info(bi.search_string)
            elif gselect == 2:
                EmailRepChecker().get_info(bi.search_string)
            elif gselect == 3:
                BreachChecker().get_info(bi.search_string)
            elif gselect == 4:
                GravatarLookup().get_info(bi.search_string)
            elif gselect == 5:
                GitHubLookup().get_info_by_email(bi.search_string)
            elif gselect == 6:
                HaveIBeenPwwnedGrabber().get_info(bi.search_string)
            elif gselect == 7:
                LinkedInGrabber().get_info(bi.search_string)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Error: {}".format(e)+bc.CEND)
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
        print(" [{}!{}] {}Domain / IP search menu{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}WHOIS + subdomains + IP lookup{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}WHOIS / RDAP{}       - {}Registrant, registrar, dates, nameservers{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}Subdomains (crt.sh){} - {}Certificate Transparency subdomain enum{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}4{}] {}IP Lookup{}          - {}Geolocation + Shodan open ports/CVEs/hostnames{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}5{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}6{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.domainmenu()
            return
        if gselect == 6:
            return
        if not bi.search_string or gselect == 5:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target domain or IP: {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 5:
                self.domainmenu()
                return
        bi.lookup = 'domain'
        print()
        try:
            if gselect == 1:
                WhoisLookup().get_info(bi.search_string)
                SubDomainGrabber().get_info(bi.search_string)
                IPLookup().get_info(bi.search_string)
            elif gselect == 2:
                WhoisLookup().get_info(bi.search_string)
            elif gselect == 3:
                SubDomainGrabber().get_info(bi.search_string)
            elif gselect == 4:
                IPLookup().get_info(bi.search_string)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Error: {}".format(e)+bc.CEND)
        input("\nPress ENTER to continue")
        self.domainmenu()

    # ─────────────────────────────── DATING ───────────────────────────────

    def datingmenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        Logo().banner()
        target = " — {}{}".format(bi.search_string, bc.CEND) if bi.search_string else ""
        print(" [{}!{}] {}Dating platform search{}{}".format(bc.CYLW, bc.CEND, bc.CBLU, target, bc.CEND))
        print('\t[{}1{}] {}All{}               - {}Run all dating modules{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}2{}] {}Dating Check{}       - {}Search 28+ platforms by username{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}3{}] {}Tinder{}             - {}Tinder profile lookup{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND, bc.CYLW, bc.CEND))
        print('\t[{}4{}] {}Reset Target{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        print('\t[{}5{}] {}Back{}'.format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
        try:
            gselect = int(input(" [{}!{}] {}Select: {} ".format(bc.CYLW, bc.CEND, bc.CBLU, bc.CEND)))
        except Exception:
            self.datingmenu()
            return
        if gselect == 5:
            return
        if not bi.search_string or gselect == 4:
            bi.search_string = input("\n  [{}PROFILE{}] {}Target username: {} ".format(bc.CBLU, bc.CEND, bc.CRED, bc.CEND))
            if gselect == 4:
                self.datingmenu()
                return
        bi.lookup = 'dating'
        print()
        try:
            if gselect == 1:
                DatingChecker().get_info(bi.search_string)
                TinderGrabber().get_info(bi.search_string)
            elif gselect == 2:
                DatingChecker().get_info(bi.search_string)
            elif gselect == 3:
                TinderGrabber().get_info(bi.search_string)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Error: {}".format(e)+bc.CEND)
        input("\nPress ENTER to continue")
        self.datingmenu()

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
