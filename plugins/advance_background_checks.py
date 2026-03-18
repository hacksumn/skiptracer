from __future__ import print_function
from __future__ import absolute_import
#
# Advancedbackgroundchecks.com scraper
#

import re
import json
import base64 as b64
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc
from time import sleep
from bs4 import BeautifulSoup

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class AdvanceBackgroundGrabber(PageGrabber):
    def check_for_captcha(self):  # Check for CAPTCHA, report to STDOUT
        captcha = self.soup.find('div', attrs={'class': 'g-recaptcha'})
        if not captcha:
            captcha = self.soup.body.findAll(text=re.compile('Custom Script'))
        if captcha:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Captcha detected, use a proxy or complete challenge in browser\n"+bc.CEND)
            return True
        return False

    def abc_try(self, lookup, information):  # Determines different URL constructs based on user supplied data
        address_list = []
        if lookup == "phone":
            try:
                phonere = re.compile(r'(\d{10}|\d{3}[\s.-]\d{3}[\s.-]\d{4})')
            except Exception:
                pass

            def makephone(information):  # Find user supplied data format, adjust as needed for URL
                try:
                    if str(information).split("-")[1]:
                        return information
                except Exception:
                    pass
                try:
                    if str(information).split(" ")[1]:
                        dashphone = '{}-{}-{}'.format(information[0:3], information[5:8], information[9:])
                        return dashphone
                except Exception:
                    pass
                try:
                    if len(information) == 10:
                        dashphone = '{}-{}-{}'.format(information[0:3], information[3:6], information[6:])
                        return dashphone
                    else:
                        print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Check search string, should be 10 digits.\n"+bc.CEND)
                        return None
                except Exception:
                    return None

            try:
                self.num = makephone(information)
                if self.num is None:
                    return
                self.url = "https://www.advancedbackgroundchecks.com/{}".format(self.num)
            except Exception as e:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Could not produce required URL.\n"+bc.CEND)
                return

        if lookup == "email":
            if str(information).split('@')[1]:
                encoded = b64.b64encode(str(information).encode('utf-8')).decode('utf-8')
                self.url = "https://www.advancedbackgroundchecks.com/emails/{}".format(encoded)

        if lookup == "name":
            if str(information).split(' ')[1]:
                age = input("[{}?{}] {}Whats the target's suspected age?{} [ex: 40{}]: ".format(bc.CRED, bc.CEND, bc.CRED, bc.CYLW, bc.CEND))
                loc = input("[{}?{}] {}Whats the target's area of residency?{} [ex: MO/11123/Chicago{}]: ".format(bc.CRED, bc.CEND, bc.CRED, bc.CYLW, bc.CEND))
                self.url = "https://www.advancedbackgroundchecks.com/name/{}_{}_age_{}".format(
                    str(information).replace(' ', '-'), loc, age)

        try:
            self.source = self.get_source(self.url)
            self.soup = self.get_dom(self.source)
            if self.check_for_captcha():
                print("Captcha Detected")
                return
        except Exception as e:
            print(e)
            return

        try:
            if self.soup.find('div', {'id': 'no-result-widgets'}):
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No results were found.\n"+bc.CEND)
                return
            checkres = self.soup.findAll("h1")
            if lookup == "phone":
                for xcheck in checkres:
                    if xcheck.text in [
                        "We could not find any results based on your search criteria.  Please review your search and try again, or try our sponsors for more information.",
                        "Top Results for " + str(self.num)
                    ]:
                        print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No results were found.\n"+bc.CEND)
                        return
            script_html = self.soup.find_all('script', type="application/ld+json")
        except Exception as findallfail:
            print("failed with findall: %s" % findallfail)
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No results were found.\n"+bc.CEND)
            return

        if len(script_html) == 3:
            script_html = script_html[2]

        person_list = []
        try:
            script_htmla = script_html.get_text().strip()
            script_htmla = script_htmla.replace("\n", "").replace("\t", "")
            person_list = json.loads(script_htmla)
        except Exception:
            pass

        for person in person_list:
            try:
                addrfirst = 0
                pnext = 0
                if pnext >= 1:
                    print(" ["+bc.CGRN+"!"+bc.CEND+"] "+bc.CRED+"Next finding: "+bc.CEND)
                self.url2 = person['@id']
                self.source2 = self.get_source(self.url2)
                self.soup2 = self.get_dom(self.source2)
                script_html2 = self.soup2.find_all('script', type="application/ld+json")
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Name: "+bc.CEND + str(person.get("name")))
                if person.get("birthDate"):
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"D.o.B: "+bc.CEND + str(person.get("birthDate")))
                if person.get("additionalName"):
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Alias: "+bc.CEND)
                    for xaka in person.get("additionalName"):
                        print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"AKA: "+bc.CEND + str(xaka))
                if len(script_html2) <= 1:
                    print(" ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Unable to re-try request... Try again later...\n"+bc.CEND)
                    return
                else:
                    script_html2 = script_html2[2]
                    script_html2 = script_html2.get_text().strip().replace("\n", "").replace("\t", "")
                    person_list2 = json.loads(script_html2)
                    if len(person_list2) > 1:
                        try:
                            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Phone: "+bc.CEND)
                            for tele in person_list2.get('telephone', []):
                                print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"#: "+bc.CEND + str(tele))
                        except Exception:
                            print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"#: Not found"+bc.CEND)
                        try:
                            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Email: "+bc.CEND)
                            for addr in person_list2.get('email', []):
                                print("   ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Addr: "+bc.CEND + str(addr))
                        except Exception:
                            print("   ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Addr: "+bc.CEND)
                if person.get("address"):
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Addresses.: "+bc.CEND)
                    for addy in person.get("address"):
                        addrfirst += 1
                        if addrfirst == 1:
                            print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Current Address: "+bc.CEND)
                        else:
                            print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Prev. Address: "+bc.CEND)
                        print("      ["+bc.CGRN+"-"+bc.CEND+"] "+bc.CRED+"Street: "+bc.CEND+str(addy.get("streetAddress")))
                        print("      ["+bc.CGRN+"-"+bc.CEND+"] "+bc.CRED+"City: "+bc.CEND+str(addy.get("addressLocality")))
                        print("      ["+bc.CGRN+"-"+bc.CEND+"] "+bc.CRED+"State: "+bc.CEND+str(addy.get("addressRegion")))
                        print("      ["+bc.CGRN+"-"+bc.CEND+"] "+bc.CRED+"ZipCode: "+bc.CEND+str(addy.get("postalCode")))
                        address_list.append({"city": addy.get("addressLocality"),
                                             "state": addy.get("addressRegion"),
                                             "zip_code": addy.get("postalCode"),
                                             "address": addy.get("streetAddress")})
                if person.get("relatedTo"):
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Related: "+bc.CEND)
                    for xrelate in [item.get("name") for item in person.get("relatedTo")]:
                        print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Known Relative: "+bc.CEND+str(xrelate))
                self.info_list.append({
                    "name": person.get("name"),
                    "birth_date": person.get("birthDate"),
                    "additional_names": person.get("additionalName"),
                    "telephone": person_list2.get('telephone', []),
                    "email": person_list2.get('email', []),
                    "address_list": address_list,
                    "related_to": [item.get("name") for item in (person.get("relatedTo") or [])]
                })
                pnext += 1
            except Exception as forloopperperson:
                print("For loop per person failed: %s" % forloopperperson)

        bi.outdata['advancedbackground'] = self.info_list
        print()
        return

    def get_info(self, lookup, information):  # Uniform call for framework
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "AdvanceBackgroundChecks" + bc.CEND)
        self.abc_try(lookup, information)
