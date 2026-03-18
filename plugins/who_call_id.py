"""Whocalld.com reverse phone lookup"""
from __future__ import print_function
from __future__ import absolute_import

import re
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi


class WhoCallIdGrabber(PageGrabber):
    def get_info(self, phone_number):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"WhoCalld"+bc.CEND)

        # Normalize phone number — strip non-digits
        digits = re.sub(r'\D', '', str(phone_number))
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        if len(digits) != 10:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Invalid phone number format. Provide 10 digits.\n"+bc.CEND)
            return

        url = 'https://whocalld.com/+1{}'.format(digits)
        source = self.get_source(url)
        if not source:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No response from WhoCalld.\n"+bc.CEND)
            return

        soup = self.get_dom(source)

        # Updated selectors based on current site structure
        phone_disp = ''
        location = ''
        carrier = ''
        city = ''
        state = ''
        name = ''

        try:
            # Phone number heading
            h1 = soup.find('h1', class_='number')
            if h1:
                phone_disp = h1.get_text(strip=True)
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Phone: "+bc.CEND+phone_disp)
        except Exception:
            pass

        try:
            # Location span
            loc_tag = soup.find('span', class_='location')
            if loc_tag:
                location = loc_tag.get_text(strip=True)
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Location: "+bc.CEND+location)
        except Exception:
            pass

        try:
            # Carrier — appears after an h3 labelled "Carrier"
            for h3 in soup.find_all('h3'):
                if 'Carrier' in h3.get_text():
                    sib = h3.find_next('span')
                    if sib:
                        carrier = sib.get_text(strip=True)
                        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Carrier: "+bc.CEND+carrier)
                    break
        except Exception:
            pass

        try:
            # Name (h2.name — legacy selector, keep as fallback)
            name_tag = soup.find('h2', class_='name')
            if name_tag:
                name = name_tag.get_text(strip=True)
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Name: "+bc.CEND+name)
        except Exception:
            pass

        try:
            city_tag = soup.find('span', class_='city')
            if city_tag:
                city = city_tag.get_text(strip=True)
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"City: "+bc.CEND+city)
        except Exception:
            pass

        try:
            state_tag = soup.find('span', class_='state')
            if state_tag:
                state = state_tag.get_text(strip=True)
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"State: "+bc.CEND+state)
        except Exception:
            pass

        if not any([phone_disp, location, carrier, name]):
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No data returned for this number.\n"+bc.CEND)
            return

        self.info_dict.update({
            'phone': phone_disp,
            'location': location,
            'carrier': carrier,
            'name': name,
            'city': city,
            'state': state,
        })
        bi.outdata['whocallid'] = self.info_dict
        print()
