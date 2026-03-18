from __future__ import print_function
from __future__ import absolute_import
#
# LinkedIn Sales Module
#
import requests
from bs4 import BeautifulSoup
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc
import json

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class LinkedInGrabber(PageGrabber):  # LinkedIn scraper for email lookups
    def get_info(self, email):
        client = requests.Session()
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "LinkedIn" + bc.CEND)
        HOMEPAGE_URL = 'https://www.linkedin.com'
        LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'
        LOGOUT_URL = 'https://www.linkedin.com/m/logout'

        try:
            source = client.get(HOMEPAGE_URL).content
            soup = self.get_dom(source)
            csrf_tag = soup.find(id="loginCsrfParam-login")
            csrf = csrf_tag['value'] if csrf_tag else ''
        except Exception:
            csrf = ''

        try:
            with open('./storage/fb_login', 'r') as fbinfo:
                login_information = json.loads(fbinfo.read())
            login_information['loginCsrfParam'] = csrf
        except Exception:
            login_information = {
                'session_key': '',
                'session_password': '',
                'loginCsrfParam': csrf,
            }

        if not login_information.get('session_key'):
            print("  ["+bc.CRED+"ATTENTION"+bc.CEND+"] " +
                  bc.CYLW+"\tThis module requires authentication to use it properly.\n\tIt will store credential pairs in plain-text."+bc.CEND)
            print("  ["+bc.CRED+"ATTENTION"+bc.CEND+"] " +
                  bc.CYLW+"This could produce a trail and identify the used account."+bc.CEND)
            print()
            savecreds = input("[{}?{}] {}Would you like to save credentials now? {}(Y/n){}]: ".format(
                bc.CRED, bc.CEND, bc.CRED, bc.CYLW, bc.CEND))
            print()
            luser = input("    ["+bc.CRED+"?"+bc.CEND+"] " +
                          bc.CYLW+"What is your throw-away linkedin username: "+bc.CEND)
            lpass = input("    ["+bc.CRED+"?"+bc.CEND+"] " +
                          bc.CYLW+"What is your throw-away linkedin password: "+bc.CEND)
            login_information = {
                'session_key': luser,
                'session_password': lpass,
                'loginCsrfParam': csrf,
            }
            if str(savecreds).lower() in ['y', 'yes']:
                try:
                    with open('./storage/fb_login', 'w') as fbinfo:
                        fbinfo.write(json.dumps({
                            'session_key': luser,
                            'session_password': lpass,
                        }))
                except Exception as failedtowrite:
                    print(("Failed to write credentials to file: %s") % failedtowrite)

        try:
            client.post(LOGIN_URL, data=login_information)
            results = client.get('https://linkedin.com/sales/gmail/profile/viewByEmail/' + str(email)).text
        except Exception as failedlinkedinauth:
            print(("  ["+bc.CRED+"X"+bc.CEND+"] " +
                   bc.CYLW+"This module did not properly authenticate: %s" +
                   bc.CEND) % failedlinkedinauth)
            return

        soup = self.get_dom(results)
        self.get_source(LOGOUT_URL)

        profile = name = company = title = location = email_found = ""

        try:
            profile_tag = soup.find('a', attrs={'class': 'li-hover-under li-txt-black-85'})
            if profile_tag:
                profile = profile_tag['href']
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Profile: "+bc.CEND + str(profile))
            else:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No LinkedIn account found.\n"+bc.CEND)
                return
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No LinkedIn account found.\n"+bc.CEND)
            return

        try:
            fname = soup.find('span', attrs={'id': 'li-profile-name'})['data-fname']
            lname = soup.find('span', attrs={'id': 'li-profile-name'})['data-lname']
            name = str(fname) + " " + str(lname)
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Name: "+bc.CEND + name)
        except Exception:
            pass

        try:
            company = soup.find('span', {'class': 'li-user-title-company'}).get_text()
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Company: "+bc.CEND + str(company))
        except Exception:
            pass

        try:
            title = soup.find('div', {'class': 'li-user-title'}).get_text()
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Title: "+bc.CEND + str(title))
        except Exception:
            pass

        try:
            location = soup.find('div', {'class': 'li-user-location'}).get_text()
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Location: "+bc.CEND + str(location))
        except Exception:
            pass

        try:
            email_found = soup.find('span', {'id': 'email'}).get_text()
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Email: "+bc.CEND + str(email_found))
        except Exception:
            pass

        self.info_dict.update({
            "profile": profile,
            "name": name,
            "location": location,
            "company": company,
            "title": title,
            "email": email_found
        })
        bi.outdata['linkedin'] = self.info_dict
        print()
        return
