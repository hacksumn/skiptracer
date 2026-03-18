from __future__ import print_function, absolute_import
#
# IP / Domain intelligence — two free APIs, no key required:
#   ip-api.com      : geolocation, ISP, ASN, timezone, mobile/proxy/hosting flags
#   Shodan InternetDB: open ports, CVEs, hostnames, tags (no API key needed)
#
import re
import socket
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

IP_PATTERN = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')


def _resolve(target):
    """Resolve hostname to IP, or return target if already an IP."""
    if IP_PATTERN.match(target):
        return target
    try:
        return socket.gethostbyname(target)
    except Exception:
        return None


def _ip_api(ip):
    """ip-api.com geolocation — free, no key, 45 req/min."""
    try:
        resp = requests.get(
            'http://ip-api.com/json/{}?fields=status,message,country,countryCode,'
            'regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query'.format(ip),
            headers=HEADERS, timeout=10
        )
        data = resp.json()
        if data.get('status') == 'success':
            return data
    except Exception:
        pass
    return {}


def _shodan_internetdb(ip):
    """Shodan InternetDB — open ports, CVEs, hostnames, tags. Free, no key."""
    try:
        resp = requests.get(
            'https://internetdb.shodan.io/{}'.format(ip),
            headers=HEADERS, timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return {'not_found': True}
    except Exception:
        pass
    return {}


class IPLookup:
    """IP address and domain intelligence using ip-api.com and Shodan InternetDB."""

    def get_info(self, target):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"IP / Domain Lookup"+bc.CEND)
        target = str(target).strip().lower()
        # Strip protocol/path if user pasted a URL
        target = re.sub(r'^https?://', '', target).split('/')[0]

        # Resolve to IP
        ip = _resolve(target)
        if not ip:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "Could not resolve '{}' to an IP address.\n".format(target)+bc.CEND)
            return

        if ip != target:
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Hostname: "+bc.CEND+target)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"IP:       "+bc.CEND+ip)
        print()

        # ── ip-api.com geolocation ───────────────────────────────────────────
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Querying ip-api.com..."+bc.CEND)
        geo = _ip_api(ip)
        if geo:
            def p(label, key):
                val = geo.get(key)
                if val:
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                          "{:<16}".format(label)+bc.CEND+str(val))

            p("Country",    'country')
            p("Region",     'regionName')
            p("City",       'city')
            p("ZIP",        'zip')
            p("Coordinates",'lat')
            lon = geo.get('lon')
            if lon:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                      "{:<16}".format("Lon")+bc.CEND+str(lon))
            p("Timezone",   'timezone')
            p("ISP",        'isp')
            p("Organization",'org')
            p("ASN",        'as')

            flags = []
            if geo.get('mobile'):  flags.append('MOBILE')
            if geo.get('proxy'):   flags.append('PROXY/VPN/TOR')
            if geo.get('hosting'): flags.append('HOSTING/DATACENTER')
            if flags:
                print("  ["+bc.CYLW+"!"+bc.CEND+"] "+bc.CRED +
                      "Flags: "+bc.CEND+bc.CYLW+", ".join(flags)+bc.CEND)
        else:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"ip-api.com returned no data."+bc.CEND)

        print()

        # ── Shodan InternetDB ────────────────────────────────────────────────
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Querying Shodan InternetDB..."+bc.CEND)
        shodan = _shodan_internetdb(ip)

        if shodan.get('not_found'):
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No Shodan data for this IP."+bc.CEND)
        elif shodan:
            ports = shodan.get('ports', [])
            if ports:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Open Ports:  "+bc.CEND +
                      ", ".join(str(p) for p in sorted(ports)))

            hostnames = shodan.get('hostnames', [])
            if hostnames:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Hostnames:   "+bc.CEND +
                      ", ".join(hostnames))

            tags = shodan.get('tags', [])
            if tags:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Tags:        "+bc.CEND +
                      ", ".join(tags))

            cpes = shodan.get('cpes', [])
            if cpes:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Software:    "+bc.CEND)
                for cpe in cpes[:10]:
                    print("    ["+bc.CGRN+"="+bc.CEND+"] "+cpe)

            vulns = shodan.get('vulns', [])
            if vulns:
                print("  ["+bc.CYLW+"!"+bc.CEND+"] "+bc.CRED+"CVEs Found:  "+bc.CEND +
                      bc.CYLW+str(len(vulns))+" vulnerabilities"+bc.CEND)
                for cve in sorted(vulns)[:15]:
                    print("    ["+bc.CYLW+"!"+bc.CEND+"] "+bc.CYLW+cve+bc.CEND)
                if len(vulns) > 15:
                    print("    ... and {} more".format(len(vulns) - 15))
        else:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Shodan InternetDB unavailable."+bc.CEND)

        print()
        try:
            bi.outdata['ip_lookup'] = {'geo': geo, 'shodan': shodan, 'ip': ip}
        except AttributeError:
            pass
