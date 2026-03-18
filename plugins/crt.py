from __future__ import absolute_import, print_function
import re
import json
import requests
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class SubDomainGrabber(PageGrabber):  # crt.sh scraper for Certificate Transparency log lookups
    def get_info(self, domain):  # returns information about a domain's subdomains
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN + "crt.sh " + bc.CEND)
        domain2 = domain.split("//")[-1].split("/")[0].split('?')[0]
        try:
            req = requests.get("https://crt.sh/?q=%.{}&output=json".format(domain2), timeout=15)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Request failed: {}\n".format(e)+bc.CEND)
            return
        if req.status_code != 200:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No results were found ...\n"+bc.CEND)
            return
        try:
            jsondata = json.loads('[{}]'.format(req.text.replace('}{', '},{')))
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Failed to parse response: {}\n".format(e)+bc.CEND)
            return

        subdomainlist = []
        for (key, value) in enumerate(jsondata):
            # name_value can contain newline-separated entries
            for name in value.get('name_value', '').split('\n'):
                subdomainlist.append(name.strip())

        subdomainlist = sorted(set(subdomainlist))

        found = []
        for subdomain in subdomainlist:
            if subdomain and not re.search(r'^\*\.', subdomain):
                print("["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Subdomain: "+bc.CEND+"{}".format(subdomain))
                found.append(subdomain)

        self.info_dict.update({"subdomains": found})
        bi.outdata['crt'] = self.info_dict

        if len(found) == 0:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No source returned, try again later ...\n"+bc.CEND)
        else:
            print()
        return
