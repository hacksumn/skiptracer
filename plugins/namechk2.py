from __future__ import print_function
#
# NameChk scraper: no1special
#
import json
import requests
import lxml.html
from bs4 import BeautifulSoup
from lxml import html

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    from requests.utils import quote
except ImportError:
    from urllib.parse import quote

from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class NameChkGrabber(PageGrabber):  # NameChk.com scraper for screenname lookups
    def get_info(self, email):  # Looks up user accounts by given screenname
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "NameChk" + bc.CEND)
        username = str(email).split("@")[0]
        ses = requests.Session()
        r = ses.get('https://namechk.com/')
        cookies = r.cookies.get_dict()
        services = ["facebook","youtube","twitter","instagram",
        "blogger","googleplus","twitch","reddit","ebay","wordpress",
        "pinterest","yelp","slack","github","basecamp","tumblr",
        "flickr","pandora","producthunt","steam","myspace",
        "foursquare","okcupid","vimeo","ustream","etsy",
        "soundcloud","bitbucket","meetup","cashme","dailymotion",
        "aboutme","disqus","medium","behance","photobucket","bitly",
        "cafemom","coderwall","fanpop","deviantart","goodreads",
        "instructables","keybase","kongregate","livejournal",
        "stumbleupon","angellist","lastfm","slideshare","tripit",
        "fotolog","paypal","dribbble","imgur","tracky","flipboard",
        "vk","kik","codecademy","roblox","gravatar","trip","pastebin",
        "coinbase","blipfm","wikipedia","ello","streamme","ifttt",
        "webcredit","codementor","soupio","fiverr","trakt","hackernews",
        "five00px","spotify","pof","houzz","contently","buzzfeed",
        "tripadvisor","hubpages","scribd","venmo","canva","creativemarket",
        "bandcamp","wikia","reverbnation","wattpad","designspiration",
        "colourlovers","eyeem","kanoworld","askfm","smashcast","badoo",
        "newgrounds","younow","patreon","mixcloud","gumroad","quora"]
        soup = self.get_dom(r.text)
        try:
            csrf = str(soup.find_all(name="meta")[-1]).split('"')[1]
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Could not find CSRF token.\n"+bc.CEND)
            return
        tree = html.fromstring(r.text)

        def get_cookie(sitecookie):
            for x in sitecookie.keys():
                return '{}:{}; '.format(x, sitecookie[x]),

        def get_token():
            return list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]

        try:
            token = get_token()
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Could not find authenticity token.\n"+bc.CEND)
            return

        headers = {"authority": "namechk.com",
        "method": "POST",
        "path": "/services/checks",
        "scheme": "https",
        "accept": "*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://namechk.com",
        "referer": "https://namechk.com/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "x-csrf-token": csrf,
        "x-requested-with": "XMLHttpRequest",
        }
        ncook = str(get_cookie(cookies)[0]) if cookies else ""
        headers['cookie'] = ncook
        data = [
            ('utf8', '%E2%9C%93'),
            ('authenticity_token', quote(token, safe="")),
            ('q', username),
            ('m', ''),
        ]
        r = ses.post('https://namechk.com/', headers=headers, data=data)
        try:
            encres = r.text.encode('ascii', 'ignore').decode('utf8')
            encresdic = json.loads(encres)
            datareq = {}
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Could not load results into JSON format.\n"+bc.CEND)
            return
        for xservice in services:
            for dictkey in encresdic.keys():
                datareq["token"] = quote(encresdic[dictkey], safe="")
            datareq['fat'] = quote(csrf, safe="")
            datastring = ""
            try:
                for datakey in datareq.keys():
                    datastring += "{}={}&".format(datakey, datareq[datakey])
                datastring += "service={}".format(xservice)
            except Exception:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Could not find CSRF token.\n"+bc.CEND)
                return
            try:
                response = ses.post('https://namechk.com/services/check', headers=headers, data=datastring)
                jload = json.loads(response.text)
                if not jload['available']:
                    if jload['callback_url'] != "":
                        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Acct Exists: "+bc.CEND+"{}".format(jload['callback_url']))
            except Exception:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Could not find required datasets.\n"+bc.CEND)
                return
        print()
        return
