from __future__ import print_function
from __future__ import absolute_import
#
# Tinder Module - illwill
#
import re
import requests
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class TinderGrabber(PageGrabber):  # tinder scraper for screenname lookups
    def get_info(self, username):  # returns information about given handle
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "Tinder" + bc.CEND)
        url = "https://www.gotinder.com/@%s" % username
        source = self.get_source(url)
        soup = self.get_dom(source)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"User: "+bc.CEND+"%s" % username)
        if soup.body.findAll(text='Looking for Someone?'):
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No Profile Found.\n"+bc.CEND)
            return

        photo = "unknown"
        name = "unknown"
        teaser = "unknown"
        age = "unknown"

        try:
            photo_tag = soup.find("img", id="user-photo")
            if photo_tag:
                photo = photo_tag.get('src', 'unknown')
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Photo: "+bc.CEND + photo)
        except Exception:
            pass

        try:
            name_tag = soup.find("span", id="name")
            if name_tag:
                name = name_tag.text
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Name: "+bc.CEND + name)
        except Exception:
            pass

        try:
            teaser_tag = soup.find("span", id="teaser")
            if teaser_tag:
                teaser = teaser_tag.text
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Bio: "+bc.CEND + teaser)
        except Exception:
            pass

        try:
            age_tag = soup.find("span", id="age")
            if age_tag:
                age = age_tag.text.replace(',', '').strip()
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Age: "+bc.CEND + age)
        except Exception:
            pass

        self.info_dict.update({
            "photo": photo,
            "name": name,
            "bio": teaser,
            "age": age
        })
        bi.outdata['tinder'] = self.info_dict
        if len(self.info_dict) == 0:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No source returned, try again later ...\n"+bc.CEND)
        else:
            print()
        return
