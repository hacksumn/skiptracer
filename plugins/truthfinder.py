from __future__ import absolute_import, print_function

#
# TruthFinder.com scraper
#
import re
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class TruthFinderGrabber(PageGrabber):
    def check_for_captcha(self):
        captcha = self.soup.find('div', attrs={'class': 'g-recaptcha'})
        if captcha is not None:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Captcha detected, use a proxy or complete challenge in browser\n"+bc.CEND)
            return True
        return False

    def truth_try(self, lookup, information):
        address_list = []
        akalist = ['unknown']
        relate = ['unknown']
        locals_list = ['unknown']

        if lookup == "phone":
            phonere = re.compile(r'(\d{10}|\d{3}[\s.-]\d{3}[\s.-]\d{4})')

            def makephone(information):
                try:
                    if str(information).split("-")[1]:
                        return '({})-{}-{}'.format(information[0:3], information[5:8], information[9:])
                except Exception:
                    pass
                try:
                    if str(information).split(" ")[1]:
                        return '({})-{}-{}'.format(information[0:3], information[5:8], information[9:])
                except Exception:
                    pass
                try:
                    if len(information) == 10:
                        return '({})-{}-{}'.format(information[0:3], information[3:6], information[6:])
                except Exception:
                    print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Did not detect a phone number\n"+bc.CEND)
                    return None

            if phonere.findall(information):
                try:
                    self.url = 'https://www.truthfinder.com/results/?phoneno={}'.format(makephone(information))
                except Exception:
                    pass

        if lookup == "name":
            citystatezip = input("[{}?{}] {}Please enter a city,state,or zip?{} [ex:(AL=Alabama|CO=Colorado){}]: ".format(
                bc.CRED, bc.CEND, bc.CRED, bc.CYLW, bc.CEND))
            gender = input("[{}?{}] {}Please enter the targets biological sex?{} [ex:(M|F){}]: ".format(
                bc.CRED, bc.CEND, bc.CRED, bc.CYLW, bc.CEND))
            age = input("[{}?{}] {}Is the person older than 30?{} [ex:(Y|n){}]: ".format(
                bc.CRED, bc.CEND, bc.CRED, bc.CYLW, bc.CEND))

            self.state = citystatezip if citystatezip else "ALL"
            self.age = "true" if age else "false"
            self.gndr = "&gender={}".format(gender) if gender else "&gender="

            parts = str(information).split(' ')
            if len(parts) >= 2:
                self.fname = parts[0]
                self.lname = parts[-1]
            else:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Failed to parse search string.\n"+bc.CEND)
                return

            self.url = ("https://www.truthfinder.com/results/?utm_source=VOTER&traffic%5Bsource%5D=VOTER"
                        "&utm_medium=pre-pop&traffic%5Bmedium%5D=pre-pop&utm_campaign=&traffic%5Bcampaign%5D=srapi%3A"
                        "&utm_term=1&traffic%5Bterm%5D=1&utm_content=&traffic%5Bcontent%5D=&s1=&s2=srapi&s3=1&s4=&s5="
                        "&city=&firstName={}&lastName={}&page=r&state={}{}&qLocation=true&qRelatives=true"
                        "&qOver30={}").format(self.fname, self.lname, self.state, self.gndr, self.age)

        self.source = self.get_source(self.url)
        self.soup = self.get_dom(self.source)

        try:
            ul = self.soup.findAll("ul")
            for xul in ul:
                perlen = len(str(xul).split("\n"))
                broken = str(xul).split("\n")
                if perlen >= 10:
                    name = "unknown"
                    age_val = "unknown"
                    try:
                        name = broken[3].split("<")[0]
                        print(("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Name: "+bc.CEND+"%s") % name)
                    except Exception:
                        pass
                    try:
                        akaloc = broken.index('aka:') + 1
                        aka = broken[akaloc].split("<")[0].replace(", ", ",")
                        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Alias: "+bc.CEND)
                        akalist = sorted(set(str(aka).split(",")))
                        for xaka in akalist:
                            print(("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"AKA: "+bc.CEND+"%s") % xaka)
                    except Exception:
                        akalist = ['unknown']
                        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"AKA: "+bc.CEND+"Unknown")
                    try:
                        ageloc = broken.index('<li class="age">') + 2
                        age_val = broken[ageloc].split(">")[1].split("<")[0]
                        if age_val:
                            print(("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Age: "+bc.CEND+"%s") % age_val)
                    except Exception:
                        age_val = 'unknown'
                        print(("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Age: "+bc.CEND+"%s") % age_val)
                    try:
                        locloc = broken.index('<li class="location">') + 2
                        locations = broken[locloc]
                        locations = locations.replace(", <span>", ":").replace("</span></li>", ",").replace("<li>", " ").replace(", </ul>", "")
                        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Location(s): "+bc.CEND)
                        locals_list = []
                        for xlocal in locations.split(","):
                            xlocal = xlocal.strip()
                            if xlocal:
                                locals_list.append(xlocal)
                                print(("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"City:State:"+bc.CEND+"%s") % xlocal)
                    except Exception:
                        locals_list = ['unknown']
                        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Location: "+bc.CEND+"Unknown")
                    try:
                        relloc = broken.index('<li class="relatives">') + 1
                        if broken[relloc].split('"')[1] == "No Relatives":
                            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Relative(s): "+bc.CEND+"Unknown")
                        else:
                            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Relative(s): "+bc.CEND)
                            relatives = broken[int(relloc) + 2].replace("\n", ",")
                            relatives = relatives.replace("</li>", ",").replace("<li>", "").replace(", </ul>", "")
                            relate = [r for r in relatives.split(",") if r.strip()]
                            for xrel in sorted(set(relate)):
                                print(("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Related: "+bc.CEND+"%s") % xrel)
                    except Exception:
                        relate = ['unknown']

                    print()
                    self.info_dict.update({
                        "name": name,
                        "age": age_val,
                        "aka": sorted(set(akalist)),
                        "locations": sorted(set(locals_list)),
                        "relatives": sorted(set(relate)),
                    })
                    bi.outdata['truthfinder'] = self.info_dict
        except Exception:
            pass

    def get_info(self, lookup, information):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "TruthFinder" + bc.CEND)
        self.truth_try(lookup, information)
