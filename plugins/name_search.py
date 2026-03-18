from __future__ import print_function, absolute_import
#
# People search by real name
# Sources:
#   Spokeo.com   — JSON-LD Person objects, server-side rendered, no auth required
#                  Returns: full name, aliases, address, profile URL
#   GitHub API   — developer identity search by real name (free, no key)
#                  Returns: username, location, email, bio, company, repos
#
import re
import json
import requests
import concurrent.futures

import cloudscraper
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

# ── US states for optional filter ─────────────────────────────────────────────
US_STATES = {
    'AL': 'Alabama',    'AK': 'Alaska',     'AZ': 'Arizona',   'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado',   'CT': 'Connecticut','DE': 'Delaware',
    'FL': 'Florida',    'GA': 'Georgia',    'HI': 'Hawaii',    'ID': 'Idaho',
    'IL': 'Illinois',   'IN': 'Indiana',    'IA': 'Iowa',      'KS': 'Kansas',
    'KY': 'Kentucky',   'LA': 'Louisiana',  'ME': 'Maine',     'MD': 'Maryland',
    'MA': 'Massachusetts','MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri',   'MT': 'Montana',    'NE': 'Nebraska',  'NV': 'Nevada',
    'NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NY': 'New York',
    'NC': 'North Carolina','ND': 'North Dakota','OH': 'Ohio',  'OK': 'Oklahoma',
    'OR': 'Oregon',     'PA': 'Pennsylvania','RI': 'Rhode Island','SC': 'South Carolina',
    'SD': 'South Dakota','TN': 'Tennessee', 'TX': 'Texas',    'UT': 'Utah',
    'VT': 'Vermont',    'VA': 'Virginia',   'WA': 'Washington','WV': 'West Virginia',
    'WI': 'Wisconsin',  'WY': 'Wyoming',    'DC': 'Washington DC',
}

GITHUB_HEADERS = {
    'User-Agent': 'runninops-osint/1.0',
    'Accept': 'application/vnd.github+json',
}

BROWSER_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/122.0.0.0 Safari/537.36'),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


# ── Spokeo ─────────────────────────────────────────────────────────────────────

def _spokeo_url(name, state=None):
    slug = name.strip().replace(' ', '-')
    if state:
        state_name = US_STATES.get(state.upper(), state)
        return 'https://www.spokeo.com/{}/{}'.format(slug, state_name.replace(' ', '-'))
    return 'https://www.spokeo.com/{}'.format(slug)


def _extract_spokeo_persons(html):
    """Pull Person JSON-LD objects and FAQ summary from Spokeo HTML."""
    persons = []
    scripts = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE
    )
    faq = {}
    for raw in scripts:
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue
        # Array of Person objects
        if isinstance(data, list) and data and data[0].get('@type') == 'Person':
            persons.extend(data)
        # FAQPage — quick summary answers
        if isinstance(data, dict) and data.get('@type') == 'FAQPage':
            for item in data.get('mainEntity', []):
                q = item.get('name', '')
                a = item.get('acceptedAnswer', {}).get('text', '')
                if 'old' in q.lower():
                    faq['age'] = a
                elif 'address' in q.lower():
                    faq['top_address'] = a
                elif 'contact' in q.lower() or 'phone' in q.lower():
                    faq['top_phone'] = a
                elif 'criminal' in q.lower():
                    faq['criminal'] = a

    # Total count from meta tag
    m = re.search(r'<meta[^>]+name=["\']result-count["\'][^>]+content=["\']([^"\']+)', html)
    total = int(m.group(1).replace(',', '')) if m else len(persons)

    return persons, faq, total


def _fmt_address(loc_list):
    """Format homeLocation list into a readable address string."""
    if not loc_list:
        return ''
    addr = loc_list[0].get('address', {}) if isinstance(loc_list[0], dict) else {}
    parts = [
        addr.get('streetAddress', ''),
        addr.get('addressLocality', ''),
        addr.get('addressRegion', ''),
        addr.get('postalCode', ''),
    ]
    return ', '.join(p for p in parts if p)


def search_spokeo(name, state=None):
    """Search Spokeo and return (persons list, faq dict, total count)."""
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    url = _spokeo_url(name, state)
    try:
        resp = scraper.get(url, headers=BROWSER_HEADERS, timeout=20)
        if resp.status_code == 404:
            return [], {}, 0
        if resp.status_code != 200:
            return [], {}, -resp.status_code
        return _extract_spokeo_persons(resp.text)
    except Exception as e:
        return [], {}, None


# ── GitHub name search ─────────────────────────────────────────────────────────

def _github_user_detail(login):
    """Fetch full profile for a GitHub login."""
    try:
        r = requests.get(
            'https://api.github.com/users/{}'.format(login),
            headers=GITHUB_HEADERS, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def search_github_by_name(name):
    """Search GitHub for accounts whose display name matches."""
    try:
        r = requests.get(
            'https://api.github.com/search/users?q={}+in:name&per_page=5'.format(
                requests.utils.quote(name)),
            headers=GITHUB_HEADERS, timeout=10
        )
        if r.status_code == 200:
            items = r.json().get('items', [])
            profiles = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                futures = {ex.submit(_github_user_detail, item['login']): item for item in items}
                for f in concurrent.futures.as_completed(futures):
                    detail = f.result()
                    if detail:
                        profiles.append(detail)
            return profiles
    except Exception:
        pass
    return []


# ── Main class ─────────────────────────────────────────────────────────────────

class NameSearch:
    """People search by real name — Spokeo (address/age/aliases) + GitHub (developer profiles)."""

    def get_info(self, name, state=None):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"People Search — "+bc.CRED+name+bc.CEND)
        if state:
            print("  ["+bc.CBLU+"i"+bc.CEND+"] "+bc.CYLW+"State filter: "+state.upper()+bc.CEND)

        results = {}

        # ── Spokeo ────────────────────────────────────────────────────────────
        print("\n  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Searching Spokeo..."+bc.CEND)
        persons, faq, total = search_spokeo(name, state)

        if total is None:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Spokeo request failed."+bc.CEND)
        elif isinstance(total, int) and total < 0:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "Spokeo returned HTTP {}.".format(-total)+bc.CEND)
        elif not persons:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No Spokeo records found."+bc.CEND)
        else:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                  "Spokeo: {:,} total matches — showing first {}:".format(total, len(persons))+bc.CEND)

            # FAQ quick-facts for the top result
            if faq.get('age'):
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Age (top result):     "+bc.CEND+faq['age'])
            if faq.get('top_address'):
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Address (top result): "+bc.CEND+faq['top_address'])
            if faq.get('top_phone') and 'no contact' not in faq['top_phone'].lower():
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Phone (top result):   "+bc.CEND+faq['top_phone'])
            if faq.get('criminal'):
                print("  ["+bc.CYLW+"!"+bc.CEND+"] "+bc.CRED+"Criminal record:      "+bc.CEND+faq['criminal'])

            print()
            spokeo_list = []
            for i, p in enumerate(persons[:30], 1):
                full_name = p.get('name', 'Unknown')
                aliases   = p.get('additionalName', [])
                address   = _fmt_address(p.get('homeLocation', []))
                url       = p.get('url', '')

                line = "  {:>3}. {}{}{}".format(i, bc.CRED, full_name, bc.CEND)
                if address:
                    line += "  — " + bc.CYLW + address + bc.CEND
                print(line)
                if aliases:
                    aka = ', '.join(aliases[:3])
                    print("       "+bc.CBLU+"AKA: "+bc.CEND+aka)
                if url:
                    print("       "+bc.CBLU+"URL: "+bc.CEND+url)

                spokeo_list.append({
                    'name': full_name,
                    'aliases': aliases,
                    'address': address,
                    'url': url,
                })

            results['spokeo'] = {'total': total, 'records': spokeo_list, 'summary': faq}

        # ── GitHub ────────────────────────────────────────────────────────────
        print("\n  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Searching GitHub by real name..."+bc.CEND)
        gh_profiles = search_github_by_name(name)

        if gh_profiles:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                  "Found {} GitHub profile(s):".format(len(gh_profiles))+bc.CEND)
            gh_list = []
            for p in gh_profiles:
                login    = p.get('login', '')
                gh_name  = p.get('name', '')
                location = p.get('location', '')
                email    = p.get('email', '')
                bio      = p.get('bio', '')
                company  = p.get('company', '')
                repos    = p.get('public_repos', '')
                profile  = p.get('html_url', '')

                print("\n    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"@{} ".format(login)+bc.CEND +
                      bc.CYLW+"({})".format(gh_name)+bc.CEND if gh_name else
                      "\n    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"@{}".format(login)+bc.CEND)
                if location: print("       "+bc.CBLU+"Location:  "+bc.CEND+location)
                if email:    print("       "+bc.CBLU+"Email:     "+bc.CEND+email)
                if company:  print("       "+bc.CBLU+"Company:   "+bc.CEND+company)
                if bio:
                    b = bio.strip()[:120]
                    print("       "+bc.CBLU+"Bio:       "+bc.CEND+b)
                if repos:    print("       "+bc.CBLU+"Repos:     "+bc.CEND+str(repos))
                if profile:  print("       "+bc.CBLU+"Profile:   "+bc.CEND+profile)
                gh_list.append(p)

            results['github'] = gh_list
        else:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No GitHub profiles found for this name."+bc.CEND)

        print()
        try:
            bi.outdata['name_search'] = results
        except AttributeError:
            pass
