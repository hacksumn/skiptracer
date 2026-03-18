from __future__ import print_function, absolute_import
#
# Gravatar profile lookup by email address
# Gravatar uses the MD5 hash of the email to identify accounts
# Returns: display name, username, bio, location, linked accounts, URLs
#
import hashlib
import requests
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

HEADERS = {
    'User-Agent': 'skiptracer-osint/2.0',
    'Accept': 'application/json',
}


class GravatarLookup:
    """Gravatar profile lookup — maps email MD5 to public profile data."""

    def get_info(self, email):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"Gravatar Lookup"+bc.CEND)
        email = str(email).strip().lower()
        email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()

        try:
            resp = requests.get(
                'https://en.gravatar.com/{}.json'.format(email_hash),
                headers=HEADERS, timeout=10
            )
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Request failed: {}\n".format(e)+bc.CEND)
            return

        if resp.status_code == 404:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No Gravatar profile found for this email.\n"+bc.CEND)
            return
        if resp.status_code != 200:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"API error: {}\n".format(resp.status_code)+bc.CEND)
            return

        try:
            data = resp.json()
            entry = data.get('entry', [{}])[0]
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Failed to parse response.\n"+bc.CEND)
            return

        def p(label, val):
            if val:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"{}: ".format(label)+bc.CEND+str(val))

        p("Email Hash",        email_hash)
        p("Display Name",      entry.get('displayName'))
        p("Username",          entry.get('preferredUsername'))
        p("Profile URL",       entry.get('profileUrl'))
        p("Avatar",            'https://www.gravatar.com/avatar/' + email_hash)

        # Name components
        name = entry.get('name', {})
        if isinstance(name, dict):
            full = name.get('formatted') or (
                (name.get('givenName', '') + ' ' + name.get('familyName', '')).strip()
            )
            p("Full Name", full)

        p("About",         entry.get('aboutMe'))
        p("Location",      entry.get('currentLocation'))
        p("Pronouns",      entry.get('pronouns'))

        # Emails (Gravatar may list verified ones)
        for em in entry.get('emails', []):
            p("Verified Email", em.get('value'))

        # Phone numbers
        for ph in entry.get('phoneNumbers', []):
            p("Phone ({})".format(ph.get('type', 'unknown')), ph.get('value'))

        # Linked accounts
        accounts = entry.get('accounts', [])
        if accounts:
            print()
            print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- Linked Accounts --"+bc.CEND)
            for acct in accounts:
                domain   = acct.get('domain', '')
                username = acct.get('username', '')
                url      = acct.get('url', '')
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                      "{:<18}".format(domain)+bc.CEND +
                      bc.CYLW+"@{} ".format(username)+bc.CEND +
                      (url if url else ''))

        # URLs
        urls = entry.get('urls', [])
        if urls:
            print()
            print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- URLs --"+bc.CEND)
            for u in urls:
                title = u.get('title', '')
                href  = u.get('value', '')
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+
                      "{}: ".format(title if title else 'URL')+bc.CEND+href)

        print()
        try:
            bi.outdata['gravatar'] = entry
        except AttributeError:
            pass
