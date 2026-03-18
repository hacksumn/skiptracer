from __future__ import print_function
from __future__ import absolute_import
#
# Dating platform search — concurrent username enumeration across 35+ sites
# Two confidence tiers:
#   HIGH : text_match / text_absent — reliable indicator confirms profile exists
#   LOW  : status-only — returns 200, but could be false positive (site-side routing)
#
import requests
import concurrent.futures
import threading
import sys

from plugins.colors import BodyColors as bc

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

# ──────────────────────────────────────────────────────────────────────────────
# Platform table
# (url_template, method, indicator, confidence)
#   method     : 'status' | 'text_match' | 'text_absent'
#   confidence : 'HIGH' | 'LOW'
# ──────────────────────────────────────────────────────────────────────────────
DATING_PLATFORMS = {

    # ── Mainstream ────────────────────────────────────────────────────────────
    'OkCupid': (
        'https://www.okcupid.com/profile/{}',
        'text_absent', "This page doesn\u2019t exist", 'HIGH'),

    'Plenty of Fish': (
        'https://www.pof.com/viewprofile.aspx?profile_id={}',
        'text_absent', 'Sorry, the profile you', 'HIGH'),

    'Match': (
        'https://www.match.com/{}',
        'text_absent', 'Page not found', 'HIGH'),

    'eHarmony': (
        'https://www.eharmony.com/dating/compatible/{}/',
        'text_absent', 'page not found', 'HIGH'),

    'Hinge': (
        'https://hinge.co/u/{}',
        'text_absent', 'not found', 'HIGH'),

    'Feeld': (
        'https://feeld.co/{}',
        'text_absent', 'not found', 'HIGH'),

    'Coffee Meets Bagel': (
        'https://coffeemeetsbagel.com/{}',
        'text_match', 'coffeemeetsbagel.com/{}', 'HIGH'),

    # ── Social / community ────────────────────────────────────────────────────
    'Badoo': (
        'https://badoo.com/en/{}',
        'text_absent', 'Page Not Found', 'HIGH'),

    'Zoosk': (
        'https://www.zoosk.com/p/{}',
        'text_match', 'zoosk.com/p/{}', 'HIGH'),

    'MeetMe': (
        'https://www.meetme.com/{}',
        'text_absent', 'Page Not Found', 'HIGH'),

    'Tagged': (
        'https://www.tagged.com/{}',
        'text_absent', 'Page Not Found', 'HIGH'),

    'Skout': (
        'https://www.skout.com/user/{}',
        'text_absent', 'not found', 'HIGH'),

    'Yubo': (
        'https://yubo.live/{}',
        'status', None, 'LOW'),

    'Wink': (
        'https://www.wink.com/profile/{}',
        'status', None, 'LOW'),

    # ── Hook-up / adult ───────────────────────────────────────────────────────
    'AdultFriendFinder': (
        'https://adultfriendfinder.com/p/{}.html',
        'text_absent', 'Profile Not Found', 'HIGH'),

    'Ashley Madison': (
        'https://www.ashleymadison.com/profile/{}',
        'text_absent', 'not found', 'HIGH'),

    'BeNaughty': (
        'https://www.benaughty.com/members/{}',
        'text_absent', 'Profile Not Found', 'HIGH'),

    'Loveaholics': (
        'https://loveaholics.com/profile/{}',
        'text_absent', 'not found', 'HIGH'),

    'Seeking': (
        'https://www.seeking.com/profile/{}',
        'text_absent', 'Profile Not Found', 'HIGH'),

    'FetLife': (
        'https://fetlife.com/users/{}',
        'text_absent', 'Page not found', 'HIGH'),

    'Swinger Zone': (
        'https://www.swingerzone.com/members/{}.html',
        'text_absent', 'not found', 'HIGH'),

    # ── LGBTQ+ ────────────────────────────────────────────────────────────────
    'Grindr': (
        'https://www.grindr.com/profile/{}',
        'status', None, 'LOW'),

    'Scruff': (
        'https://www.scruff.com/en/profiles/{}',
        'status', None, 'LOW'),

    'Hornet': (
        'https://hornet.com/@{}',
        'text_absent', 'Page not found', 'HIGH'),

    'Her': (
        'https://weareher.com/{}',
        'status', None, 'LOW'),

    'Adam4Adam': (
        'https://www.adam4adam.com/profiles/view/{}',
        'text_absent', 'not found', 'HIGH'),

    'Growlr': (
        'https://www.growlrapp.com/profile/{}',
        'status', None, 'LOW'),

    'Taimi': (
        'https://taimi.com/{}',
        'status', None, 'LOW'),

    # ── Niche / senior / religious ────────────────────────────────────────────
    'SilverSingles': (
        'https://www.silversingles.com/profile/{}',
        'status', None, 'LOW'),

    'OurTime': (
        'https://www.ourtime.com/profile/{}',
        'status', None, 'LOW'),

    'Cougar Life': (
        'https://www.cougarlife.com/{}',
        'status', None, 'LOW'),

    'Jdate': (
        'https://www.jdate.com/en-us/profile/{}',
        'status', None, 'LOW'),

    'Christian Mingle': (
        'https://www.christianmingle.com/en-us/profile/{}',
        'status', None, 'LOW'),

    'Black People Meet': (
        'https://www.blackpeoplemeet.com/en-us/profile/{}',
        'status', None, 'LOW'),

    'WooPlus': (
        'https://www.wooplus.com/profile/{}',
        'status', None, 'LOW'),

    'Clover': (
        'https://clover.co/u/{}',
        'text_absent', 'not found', 'HIGH'),

    # ── Reddit (dating communities) ───────────────────────────────────────────
    'Reddit': (
        'https://www.reddit.com/user/{}/about.json',
        'text_match', '"name":"{}', 'HIGH'),

    'Reddit r/r4r': (
        'https://www.reddit.com/user/{}/submitted.json?limit=5',
        'text_match', '"subreddit":"r4r"', 'HIGH'),
}

# Platforms with no web-accessible profiles — mobile-only or login-gated
MOBILE_ONLY = {
    'Tinder':  'Use the Tinder module (Username menu) — requires phone-based token',
    'Bumble':  'Mobile-only, no public profile URLs',
    '3Fun':    'Mobile-only app',
    'Hily':    'Mobile-only app',
    'Happn':   'Mobile-only app',
    'Raya':    'Private, invite-only — no public profiles',
    'Thursday':'Mobile-only, profiles deleted after 24h',
}

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/122.0.0.0 Safari/537.36'),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Cache-Control': 'no-cache',
}

_print_lock = threading.Lock()


def _safe_print(msg):
    with _print_lock:
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'replace').decode('ascii'))
        sys.stdout.flush()


def _extract_profile_details(url, html):
    """Try to pull name/age/location/bio from a found profile page."""
    if not HAS_BS4 or not html:
        return {}
    details = {}
    try:
        soup = BeautifulSoup(html, 'lxml')
        # Generic: og:title / og:description / og:image (works on many sites)
        og_title = soup.find('meta', property='og:title')
        og_desc  = soup.find('meta', property='og:description')
        og_img   = soup.find('meta', property='og:image')
        if og_title and og_title.get('content'):
            details['title'] = og_title['content'].strip()
        if og_desc and og_desc.get('content'):
            details['description'] = og_desc['content'].strip()
        if og_img and og_img.get('content'):
            details['photo'] = og_img['content'].strip()
        # Page <title> fallback
        if not details.get('title') and soup.title:
            details['title'] = soup.title.string.strip() if soup.title.string else ''
    except Exception:
        pass
    return details


def _check_platform(args):
    """Worker: check one platform for the given username. Returns full result tuple."""
    name, (url_tpl, method, indicator, confidence), username = args
    url = url_tpl.format(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        html = resp.text

        if method == 'status':
            found = resp.status_code == 200
        elif method == 'text_match':
            needle = indicator.format(username) if '{}' in indicator else indicator
            found = resp.status_code == 200 and needle in html
        elif method == 'text_absent':
            found = resp.status_code == 200 and indicator not in html
        else:
            found = False

        details = _extract_profile_details(url, html) if found else {}
        return name, found, url, confidence, details, None

    except requests.exceptions.Timeout:
        return name, False, url, confidence, {}, 'timeout'
    except Exception as e:
        return name, False, url, confidence, {}, str(e)


def _divider(char='=', width=60):
    return char * width


class DatingChecker:
    """Concurrent dating platform search across 35+ sites by username."""

    def get_info(self, username):
        username = str(username).strip().lstrip('@')

        print("\n" + _divider())
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN +
              "Dating Platform Search — target: "+bc.CRED+"{}".format(username)+bc.CEND)
        print(_divider())

        # Show mobile-only platforms up front
        print("\n  ["+bc.CBLU+"i"+bc.CEND+"] "+bc.CYLW+"Cannot check by username (mobile-only / login-gated):"+bc.CEND)
        for app, reason in MOBILE_ONLY.items():
            print("    "+bc.CBLU+"•"+bc.CEND+" "+bc.CRED+"{:<16}".format(app)+bc.CEND+
                  bc.CYLW+" {}".format(reason)+bc.CEND)

        print("\n  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW +
              "Scanning {} platforms concurrently — results appear as they arrive...\n".format(
                  len(DATING_PLATFORMS))+bc.CEND)
        print(_divider())

        tasks = [(name, data, username) for name, data in DATING_PLATFORMS.items()]
        found_high   = {}   # HIGH confidence hits
        found_low    = {}   # LOW  confidence hits
        not_found    = []
        errors       = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(_check_platform, t): t[0] for t in tasks}
            for future in concurrent.futures.as_completed(futures):
                name, found, url, confidence, details, err = future.result()

                if err == 'timeout':
                    errors.append((name, 'timeout'))
                    _safe_print("  ["+bc.CYLW+"T"+bc.CEND+"] "+bc.CYLW+
                                "{:<22} — timeout".format(name)+bc.CEND)
                elif found:
                    if confidence == 'HIGH':
                        found_high[name] = (url, details)
                        _safe_print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CGRN+
                                    "FOUND (HIGH)   "+bc.CEND+bc.CRED +
                                    "{:<22}".format(name)+bc.CEND+" "+url)
                    else:
                        found_low[name] = (url, details)
                        _safe_print("  ["+bc.CYLW+"~"+bc.CEND+"] "+bc.CYLW +
                                    "POSSIBLE (LOW) "+bc.CEND+bc.CRED +
                                    "{:<22}".format(name)+bc.CEND+" "+url)
                else:
                    not_found.append(name)
                    _safe_print("  ["+bc.CRED+"X"+bc.CEND+"] "+
                                "{:<22} — not found".format(name))

        # ── Final Summary ─────────────────────────────────────────────────────
        print("\n" + _divider())
        print("["+bc.CGRN+"RESULTS"+bc.CEND+"] "+bc.CCYN +
              "Dating Search Summary — {}".format(username)+bc.CEND)
        print(_divider())

        if found_high:
            print("\n  "+bc.CGRN+"[ HIGH CONFIDENCE — Profile confirmed ]"+bc.CEND)
            print("  " + "-" * 56)
            _generic_titles = {'home page', 'home', 'sign in', 'login', 'log in',
                               'register', 'sign up', '404', 'not found', 'error'}
            for i, (platform, (url, details)) in enumerate(found_high.items(), 1):
                title = details.get('title', '')
                # Flag if title looks like a homepage/login redirect (false positive)
                is_generic = title.lower().strip().rstrip('.') in _generic_titles
                marker = bc.CYLW + " [verify - generic page title]" + bc.CEND if is_generic else ''
                print("  {:>2}. {}{}{}{}{}{}".format(
                    i, bc.CRED, platform.ljust(22), bc.CEND, bc.CYLW, url, bc.CEND) + marker)
                if title and not is_generic:
                    print("      "+bc.CBLU+"Title  : "+bc.CEND+title)
                if details.get('description') and not is_generic:
                    desc = details['description']
                    if len(desc) > 120:
                        desc = desc[:120] + '...'
                    print("      "+bc.CBLU+"Bio    : "+bc.CEND+desc)
                if details.get('photo') and not is_generic:
                    print("      "+bc.CBLU+"Photo  : "+bc.CEND+details['photo'])

        if found_low:
            print("\n  "+bc.CYLW+"[ LOW CONFIDENCE — Status 200 only, verify manually ]"+bc.CEND)
            print("  " + "-" * 56)
            for platform, (url, details) in found_low.items():
                print("  "+bc.CYLW+"  • "+bc.CRED+"{:<22}".format(platform)+bc.CEND +
                      bc.CYLW+" {}".format(url)+bc.CEND)

        if not found_high and not found_low:
            print("\n  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "No dating profiles found for username: {}".format(username)+bc.CEND)
        else:
            total = len(found_high) + len(found_low)
            print("\n  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW +
                  "Total: {} confirmed | {} possible | {} not found | {} timeout".format(
                      len(found_high), len(found_low), len(not_found), len(errors))+bc.CEND)

        print(_divider() + "\n")

        try:
            bi.outdata['dating_check'] = {
                'confirmed': {p: u for p, (u, _) in found_high.items()},
                'possible':  {p: u for p, (u, _) in found_low.items()},
            }
        except AttributeError:
            pass
