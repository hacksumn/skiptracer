from __future__ import print_function
from __future__ import absolute_import
#
# GitHub API lookup — no key required, returns full public profile
#
import requests
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

HEADERS = {
    'User-Agent': 'runninops-osint/1.0',
    'Accept': 'application/vnd.github+json',
}


class GitHubLookup:
    """Looks up a GitHub user by username or searches by email."""

    def _print_user(self, user):
        fields = [
            ('Name',       user.get('name')),
            ('Bio',        user.get('bio')),
            ('Company',    user.get('company')),
            ('Location',   user.get('location')),
            ('Email',      user.get('email')),
            ('Website',    user.get('blog')),
            ('Twitter',    user.get('twitter_username')),
            ('Followers',  user.get('followers')),
            ('Following',  user.get('following')),
            ('Repos',      user.get('public_repos')),
            ('Gists',      user.get('public_gists')),
            ('Created',    user.get('created_at', '').split('T')[0]),
            ('Profile',    user.get('html_url')),
            ('Avatar',     user.get('avatar_url')),
        ]
        for label, val in fields:
            if val:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"{}: ".format(label)+bc.CEND+str(val))

    def get_info(self, username):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"GitHub Lookup"+bc.CEND)
        username = str(username).strip().lstrip('@')

        # Direct user lookup
        try:
            resp = requests.get(
                'https://api.github.com/users/{}'.format(username),
                headers=HEADERS, timeout=10
            )
            if resp.status_code == 200:
                user = resp.json()
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"GitHub account found:"+bc.CEND)
                self._print_user(user)
                bi.outdata['github'] = user
                print()
                return
            elif resp.status_code == 404:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No GitHub account found for: {}\n".format(username)+bc.CEND)
            else:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"GitHub API error: {}\n".format(resp.status_code)+bc.CEND)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"GitHub request failed: {}\n".format(e)+bc.CEND)

    def get_info_by_email(self, email):
        """Search GitHub for accounts associated with an email address."""
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"GitHub Email Search"+bc.CEND)
        try:
            resp = requests.get(
                'https://api.github.com/search/users?q={}+in:email'.format(email),
                headers=HEADERS, timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get('items', [])
                if items:
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Found {} GitHub account(s) linked to email:".format(len(items))+bc.CEND)
                    for item in items:
                        login = item.get('login', '')
                        url = item.get('html_url', '')
                        print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"User: "+bc.CEND+login+" — "+url)
                        # Fetch full profile
                        self.get_info(login)
                    return
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No GitHub accounts found for this email.\n"+bc.CEND)
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"GitHub search failed: {}\n".format(e)+bc.CEND)
