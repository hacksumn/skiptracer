from __future__ import print_function
from __future__ import absolute_import
#
# Breach data aggregator — LeakCheck.io + XposedOrNot
# Both APIs are free and require no API key
#
import requests
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/122.0.0.0 Safari/537.36'),
    'Accept': 'application/json',
}


def _leakcheck(email):
    """Query LeakCheck.io public API. Returns list of {name, date} dicts."""
    try:
        resp = requests.get(
            'https://leakcheck.io/api/public?check={}'.format(email),
            headers=HEADERS, timeout=12
        )
        data = resp.json()
        if data.get('success') and data.get('found', 0) > 0:
            return data.get('sources', []), data.get('found', 0)
    except Exception:
        pass
    return [], 0


def _xposedornot(email):
    """Query XposedOrNot API. Returns list of breach names."""
    try:
        resp = requests.get(
            'https://api.xposedornot.com/v1/check-email/{}'.format(email),
            headers=HEADERS, timeout=12
        )
        if resp.status_code == 200:
            data = resp.json()
            breaches = data.get('breaches', [])
            if breaches and isinstance(breaches[0], list):
                return breaches[0]
            return breaches
    except Exception:
        pass
    return []


class BreachChecker:
    """Checks email against LeakCheck.io and XposedOrNot breach databases."""

    def get_info(self, email):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"Breach Check"+bc.CEND)

        all_breaches = {}

        # --- LeakCheck ---
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Querying LeakCheck.io..."+bc.CEND)
        lc_sources, lc_count = _leakcheck(email)
        if lc_sources:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"LeakCheck found {} breach(es):".format(lc_count)+bc.CEND)
            for src in lc_sources:
                name = src.get('name', str(src))
                date = src.get('date', '')
                label = "{} ({})".format(name, date) if date else name
                print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Breach: "+bc.CEND+label)
                all_breaches[name] = date
        else:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"LeakCheck: No results or unavailable"+bc.CEND)

        print()

        # --- XposedOrNot ---
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Querying XposedOrNot..."+bc.CEND)
        xon_breaches = _xposedornot(email)
        if xon_breaches:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"XposedOrNot found {} breach(es):".format(len(xon_breaches))+bc.CEND)
            for name in xon_breaches:
                print("    ["+bc.CGRN+"="+bc.CEND+"] "+bc.CRED+"Breach: "+bc.CEND+str(name))
                if name not in all_breaches:
                    all_breaches[str(name)] = ''
        else:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"XposedOrNot: No results or unavailable"+bc.CEND)

        print()
        if all_breaches:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+"Total unique breaches found: {}\n".format(len(all_breaches))+bc.CEND)
        else:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+"No breaches found for this email address.\n"+bc.CEND)

        bi.outdata['breach_check'] = all_breaches
        return
