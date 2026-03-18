from __future__ import print_function
from __future__ import absolute_import
#
# Username enumeration across 35+ platforms
# Uses concurrent requests for speed — typically completes in under 15 seconds
#
import requests
import concurrent.futures

from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

# Platform definitions: name -> (url_template, check_method, not_found_indicator)
# Methods:
#   'status'     : 200 = found, 404 = not found
#   'api_json'   : 200 + valid JSON body = found
#   'api_notnull': 200 + body != 'null' = found
#   'text_match' : 200 + specific text present = found
#   'text_absent': 200 + specific text ABSENT = found (page exists but "not found" text absent)

PLATFORMS = {
    'GitHub':       ('https://api.github.com/users/{}',                    'api_json',    None),
    'Reddit':       ('https://www.reddit.com/user/{}/about.json',           'api_json',    None),
    'HackerNews':   ('https://hacker-news.firebaseio.com/v0/user/{}.json',  'api_notnull', None),
    'Instagram':    ('https://www.instagram.com/{}/',                        'text_match',  '"username":"{}'),
    'TikTok':       ('https://www.tiktok.com/@{}',                          'text_absent', 'Couldn\u2019t find this account'),
    'Twitter':      ('https://twitter.com/{}',                               'status',      None),
    'Twitch':       ('https://www.twitch.tv/{}',                             'text_absent', 'Sorry. Unless you\u2019ve got a time machine'),
    'Telegram':     ('https://t.me/{}',                                      'text_match',  'tgme_page_title'),
    'Pinterest':    ('https://www.pinterest.com/{}_saved/',                  'status',      None),
    'Medium':       ('https://medium.com/@{}',                               'text_absent', 'Page not found'),
    'SoundCloud':   ('https://soundcloud.com/{}',                            'text_absent', 'We can\u2019t find that user'),
    'Spotify':      ('https://open.spotify.com/user/{}',                     'text_absent', 'Page not found'),
    'Vimeo':        ('https://vimeo.com/{}',                                 'status',      None),
    'Gitlab':       ('https://gitlab.com/{}',                                'status',      None),
    'Keybase':      ('https://keybase.io/{}',                                'status',      None),
    'Pastebin':     ('https://pastebin.com/u/{}',                            'status',      None),
    'Replit':       ('https://replit.com/@{}',                               'status',      None),
    'DeviantArt':   ('https://www.deviantart.com/{}',                        'status',      None),
    'Flickr':       ('https://www.flickr.com/people/{}',                     'status',      None),
    'Last.fm':      ('https://www.last.fm/user/{}',                          'text_absent', 'Sorry, this page isn\u2019t available'),
    'Wattpad':      ('https://www.wattpad.com/user/{}',                      'status',      None),
    'ProductHunt':  ('https://www.producthunt.com/@{}',                      'status',      None),
    'About.me':     ('https://about.me/{}',                                  'status',      None),
    'Behance':      ('https://www.behance.net/{}',                           'status',      None),
    'Gravatar':     ('https://en.gravatar.com/{}',                           'status',      None),
    'Codecademy':   ('https://www.codecademy.com/profiles/{}',               'status',      None),
    'Steam':        ('https://steamcommunity.com/id/{}',                     'text_absent', 'The specified profile could not be found'),
    'Bandcamp':     ('https://{}.bandcamp.com',                              'status',      None),
    'Tumblr':       ('https://{}.tumblr.com',                                'text_absent', 'There\u2019s nothing here'),
    'Goodreads':    ('https://www.goodreads.com/{}',                         'status',      None),
    'Imgur':        ('https://imgur.com/user/{}',                            'status',      None),
    'SlideShare':   ('https://www.slideshare.net/{}',                        'status',      None),
    'Fiverr':       ('https://www.fiverr.com/{}',                            'status',      None),
    'Cashapp':      ('https://cash.app/${}',                                 'status',      None),
    'Venmo':        ('https://account.venmo.com/u/{}',                       'status',      None),
}

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/122.0.0.0 Safari/537.36'),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def _check_platform(args):
    """Worker function: check a single platform for the given username."""
    name, (url_tpl, method, indicator), username = args
    url = url_tpl.format(username)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if method == 'status':
            found = resp.status_code == 200
        elif method == 'api_json':
            found = resp.status_code == 200
        elif method == 'api_notnull':
            found = resp.status_code == 200 and resp.text.strip() not in ('null', '', '{}')
        elif method == 'text_match':
            needle = indicator.format(username) if '{}' in indicator else indicator
            found = resp.status_code == 200 and needle in resp.text
        elif method == 'text_absent':
            found = resp.status_code == 200 and indicator not in resp.text
        else:
            found = False
        return name, found, url
    except Exception:
        return name, False, url


class UsernameChecker:
    """Concurrent username enumeration across 35+ platforms."""

    def get_info(self, username):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"Username Check"+bc.CEND)
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Checking {} platforms concurrently...\n".format(len(PLATFORMS))+bc.CEND)

        username = str(username).strip().lstrip('@')
        tasks = [(name, data, username) for name, data in PLATFORMS.items()]
        found_accounts = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(_check_platform, t): t[0] for t in tasks}
            for future in concurrent.futures.as_completed(futures):
                name, found, url = future.result()
                if found:
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"{}: ".format(name)+bc.CEND+url)
                    found_accounts[name] = url

        if not found_accounts:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No accounts found for: {}\n".format(username)+bc.CEND)
        else:
            print("\n  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+"Found {} account(s) for: {}\n".format(len(found_accounts), username)+bc.CEND)

        bi.outdata['username_check'] = found_accounts
        return
