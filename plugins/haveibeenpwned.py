from __future__ import print_function
from __future__ import absolute_import
#
#   haveibeenpwned scraper - returns breach name and date for email
#   Uses HIBP API v3 — requires an API key from https://haveibeenpwned.com/API/Key
#   Set HIBP_API_KEY environment variable or provide key in ./storage/hibp_key.txt
#

import os
import requests
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


def _load_api_key():
    # Try environment variable first
    key = os.environ.get('HIBP_API_KEY', '')
    if key:
        return key
    # Try local file
    try:
        with open('./storage/hibp_key.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        pass
    return ''


class HaveIBeenPwwnedGrabber(PageGrabber):
    def get_info(self, email):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "HaveIbeenPwned" + bc.CEND)
        api_key = _load_api_key()
        if not api_key:
            print("  ["+bc.CRED+"!"+bc.CEND+"] "+bc.CYLW +
                  "HIBP v3 requires an API key. Get one at https://haveibeenpwned.com/API/Key\n"
                  "  Set HIBP_API_KEY env var or place key in ./storage/hibp_key.txt\n" + bc.CEND)
            return

        url = 'https://haveibeenpwned.com/api/v3/breachedaccount/{}'.format(email)
        headers = {
            'hibp-api-key': api_key,
            'user-agent': self.ua,
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Request failed: {}\n".format(e)+bc.CEND)
            return

        if resp.status_code == 404:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+"No breaches found for this email.\n"+bc.CEND)
            return
        if resp.status_code == 401:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Invalid or missing API key.\n"+bc.CEND)
            return
        if resp.status_code == 429:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Rate limited — try again later.\n"+bc.CEND)
            return
        if resp.status_code != 200:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Failed to access HIBP (status {})\n".format(resp.status_code)+bc.CEND)
            return

        try:
            breaches = resp.json()
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Failed to parse response.\n"+bc.CEND)
            return

        for result in breaches:
            try:
                breach_date = result.get('BreachDate', 'Unknown')
                domain = result.get('Domain', 'Unknown')
                title = result.get('Title', 'Unknown')
                exposes = result.get('DataClasses', [])
                self.info_dict[title] = {
                    "BreachDate": breach_date,
                    "Domain": domain,
                    "DataExposed": exposes
                }
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Dump Name: "+bc.CEND + title)
                print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Domain: "+bc.CEND + domain)
                print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Breach: "+bc.CEND + breach_date)
                print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Exposes: "+bc.CEND)
                for xpos in exposes:
                    print("      ["+bc.CGRN+"-"+bc.CEND+"] "+bc.CRED+"DataSet: "+bc.CEND + xpos)
            except Exception as e:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Error processing breach: {}\n".format(e)+bc.CEND)

        bi.outdata['haveibeenpwned'] = self.info_dict
        print()
