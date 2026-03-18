from __future__ import print_function
from __future__ import absolute_import
#
# Dating platform username enumeration — concurrent HTTP checks
# Covers platforms with publicly accessible profile URLs.
# Note: Tinder, Bumble, 3Fun are mobile-only apps with no public profile URLs —
#       Tinder is handled by the separate Tinder module (requires phone token).
#
import requests
import concurrent.futures

from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

# Platform definitions: name -> (url_template, check_method, indicator)
# Methods:
#   'status'     : HTTP 200 = found
#   'text_match' : 200 + specific text PRESENT = found
#   'text_absent': 200 + specific text ABSENT  = found

DATING_PLATFORMS = {
    # ── Major mainstream ──────────────────────────────────────────────────────
    'OkCupid':           ('https://www.okcupid.com/profile/{}',
                          'text_absent', 'This page doesn\u2019t exist'),
    'Plenty of Fish':    ('https://www.pof.com/viewprofile.aspx?profile_id={}',
                          'text_absent', 'Sorry'),
    'Match':             ('https://www.match.com/{}',
                          'text_absent', 'Page Not Found'),
    'eHarmony':          ('https://www.eharmony.com/dating/compatible/{}/',
                          'status', None),
    'Hinge':             ('https://hinge.co/u/{}',
                          'text_absent', 'not found'),
    'Feeld':             ('https://feeld.co/{}',
                          'text_absent', 'not found'),
    'Coffee Meets Bagel':('https://coffeemeetsbagel.com/{}',
                          'status', None),

    # ── Hook-up / adult ───────────────────────────────────────────────────────
    'AdultFriendFinder': ('https://adultfriendfinder.com/p/{}.html',
                          'text_absent', 'Profile Not Found'),
    'Ashley Madison':    ('https://www.ashleymadison.com/profile/{}',
                          'status', None),
    'BeNaughty':         ('https://www.benaughty.com/members/{}',
                          'text_absent', 'Profile Not Found'),
    'Loveaholics':       ('https://loveaholics.com/profile/{}',
                          'text_absent', 'not found'),
    'Seeking':           ('https://www.seeking.com/profile/{}',
                          'text_absent', 'Profile Not Found'),
    'FetLife':           ('https://fetlife.com/users/{}',
                          'text_absent', 'Page not found'),

    # ── LGBTQ+ / niche ────────────────────────────────────────────────────────
    'Grindr':            ('https://www.grindr.com/profile/{}',
                          'status', None),
    'Scruff':            ('https://www.scruff.com/en/profiles/{}',
                          'status', None),
    'Her':               ('https://weareher.com/{}',
                          'status', None),
    'Chappy':            ('https://www.chappy.com/user/{}',
                          'status', None),

    # ── Social / community ────────────────────────────────────────────────────
    'Badoo':             ('https://badoo.com/en/{}',
                          'text_absent', 'Page Not Found'),
    'Zoosk':             ('https://www.zoosk.com/p/{}',
                          'status', None),
    'MeetMe':            ('https://www.meetme.com/{}',
                          'text_absent', 'Page Not Found'),
    'Tagged':            ('https://www.tagged.com/{}',
                          'text_absent', 'Page Not Found'),
    'Skout':             ('https://www.skout.com/user/{}',
                          'status', None),
    'Wink':              ('https://www.wink.com/profile/{}',
                          'status', None),
    'Yubo':              ('https://yubo.live/{}',
                          'status', None),

    # ── Senior / niche demographics ───────────────────────────────────────────
    'SilverSingles':     ('https://www.silversingles.com/profile/{}',
                          'status', None),
    'OurTime':           ('https://www.ourtime.com/profile/{}',
                          'status', None),
    'Cougar Life':       ('https://www.cougarlife.com/{}',
                          'status', None),

    # ── Reddit dating communities (username search) ───────────────────────────
    'Reddit':            ('https://www.reddit.com/user/{}/about.json',
                          'text_absent', '"error"'),
}

# Platforms that are mobile-only with no public web profile URLs
MOBILE_ONLY = ['Tinder', 'Bumble', '3Fun', 'Hily', 'Happn', 'Taimi']

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/122.0.0.0 Safari/537.36'),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def _check_platform(args):
    """Worker: check one dating platform for the given username."""
    name, (url_tpl, method, indicator), username = args
    url = url_tpl.format(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        if method == 'status':
            found = resp.status_code == 200
        elif method == 'text_match':
            found = resp.status_code == 200 and indicator in resp.text
        elif method == 'text_absent':
            found = resp.status_code == 200 and indicator not in resp.text
        else:
            found = False
        return name, found, url
    except Exception:
        return name, False, url


class DatingChecker:
    """Concurrent dating platform search across 28+ sites by username."""

    def get_info(self, username):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"Dating Platform Search"+bc.CEND)

        # Note mobile-only apps upfront
        print("  ["+bc.CBLU+"i"+bc.CEND+"] "+bc.CYLW +
              "Mobile-only (no public URL, use Tinder module for Tinder): " +
              ", ".join(MOBILE_ONLY)+bc.CEND)
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW +
              "Checking {} platforms concurrently...\n".format(len(DATING_PLATFORMS))+bc.CEND)

        username = str(username).strip().lstrip('@')
        tasks = [(name, data, username) for name, data in DATING_PLATFORMS.items()]
        found_accounts = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(_check_platform, t): t[0] for t in tasks}
            for future in concurrent.futures.as_completed(futures):
                name, found, url = future.result()
                if found:
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                          "{}: ".format(name)+bc.CEND+url)
                    found_accounts[name] = url

        print()
        if not found_accounts:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "No dating profiles found for: {}\n".format(username)+bc.CEND)
        else:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW +
                  "Found {} dating profile(s) for: {}\n".format(
                      len(found_accounts), username)+bc.CEND)

        bi.outdata['dating_check'] = found_accounts
