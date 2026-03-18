from __future__ import print_function, absolute_import
#
# EmailRep.io — free email reputation API, no API key required
# Returns: reputation score, breach status, social profiles, spam/blacklist,
#          first/last seen, deliverability, spoofability, domain reputation
#
import requests
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

HEADERS = {
    'User-Agent': 'runninops-osint/1.0',
    'Accept': 'application/json',
}


class EmailRepChecker:
    """EmailRep.io free email reputation and intelligence lookup."""

    def get_info(self, email):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"EmailRep.io Lookup"+bc.CEND)
        email = str(email).strip().lower()

        try:
            resp = requests.get(
                'https://emailrep.io/{}'.format(email),
                headers=HEADERS, timeout=12
            )
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Request failed: {}\n".format(e)+bc.CEND)
            return

        if resp.status_code == 400:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Invalid email address.\n"+bc.CEND)
            return
        if resp.status_code != 200:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"API error: {}\n".format(resp.status_code)+bc.CEND)
            return

        try:
            data = resp.json()
        except Exception:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Failed to parse response.\n"+bc.CEND)
            return

        details = data.get('details', {})

        def yn(val):
            return bc.CGRN+"YES"+bc.CEND if val else bc.CRED+"no"+bc.CEND

        def flag(label, val):
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"{}: ".format(label)+bc.CEND+str(val))

        # Core reputation
        reputation = data.get('reputation', 'none')
        rep_color = bc.CGRN if reputation == 'high' else (bc.CYLW if reputation == 'medium' else bc.CRED)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Email:       "+bc.CEND+email)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Reputation:  "+bc.CEND+rep_color+reputation.upper()+bc.CEND)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Suspicious:  "+bc.CEND+yn(data.get('suspicious', False)))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"References:  "+bc.CEND+str(data.get('references', 0))+" sources know this address")

        # Breach / credentials
        print()
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- Breach & Security --"+bc.CEND)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Data Breach:         "+bc.CEND+yn(details.get('data_breach')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Credentials Leaked:  "+bc.CEND+yn(details.get('credentials_leaked')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Credentials Recent:  "+bc.CEND+yn(details.get('credentials_leaked_recent')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Malicious Activity:  "+bc.CEND+yn(details.get('malicious_activity')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Blacklisted:         "+bc.CEND+yn(details.get('blacklisted')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Spam:                "+bc.CEND+yn(details.get('spam')))

        # Email properties
        print()
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- Email Properties --"+bc.CEND)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Free Provider:  "+bc.CEND+yn(details.get('free_provider')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Disposable:     "+bc.CEND+yn(details.get('disposable')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Deliverable:    "+bc.CEND+yn(details.get('deliverable')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Spoofable:      "+bc.CEND+yn(details.get('spoofable')))
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Valid MX:       "+bc.CEND+yn(details.get('valid_mx')))

        # Activity timeline
        first_seen = details.get('first_seen', '')
        last_seen  = details.get('last_seen', '')
        if first_seen or last_seen:
            print()
            print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- Activity Timeline --"+bc.CEND)
            if first_seen:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"First Seen: "+bc.CEND+first_seen)
            if last_seen:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Last Seen:  "+bc.CEND+last_seen)

        # Social profiles
        profiles = details.get('profiles', [])
        if profiles:
            print()
            print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- Known Social Profiles --"+bc.CEND)
            for p in profiles:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Profile: "+bc.CEND+str(p))

        print()
        try:
            bi.outdata['emailrep'] = data
        except AttributeError:
            pass
