from __future__ import print_function, absolute_import
#
# Domain WHOIS via RDAP (Registration Data Access Protocol)
# Free US government standard API — no key, no scraping, structured JSON
# Covers all gTLDs (.com, .net, .org, etc.) via rdap.org aggregator
# Also queries ViewDNS.info for reverse WHOIS by email (free public search)
#
import re
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


def _rdap_domain(domain):
    """Fetch RDAP record for a domain. Returns raw dict."""
    try:
        resp = requests.get(
            'https://rdap.org/domain/{}'.format(domain),
            headers=HEADERS, timeout=15, allow_redirects=True
        )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return {'_not_found': True}
    except Exception:
        pass
    return {}


def _extract_vcard(vcard_array):
    """Pull name/org/email/address from a vCard array."""
    info = {}
    if not isinstance(vcard_array, list):
        return info
    for item in vcard_array:
        if not isinstance(item, list):
            continue
        for field in item:
            if not isinstance(field, list) or len(field) < 4:
                continue
            ftype = field[0]
            fval  = field[3]
            if ftype == 'fn':
                info['name'] = fval
            elif ftype == 'org':
                info['org'] = fval if isinstance(fval, str) else (fval[0] if fval else '')
            elif ftype == 'email':
                info.setdefault('emails', []).append(fval)
            elif ftype == 'adr':
                if isinstance(fval, list):
                    parts = [str(p).strip() for p in fval if str(p).strip()]
                    info['address'] = ', '.join(parts)
                else:
                    info['address'] = str(fval)
            elif ftype == 'tel':
                info.setdefault('phones', []).append(fval)
    return info


def _parse_entities(entities, role_filter=None):
    """Recursively extract entity info from RDAP entities list."""
    results = []
    for entity in (entities or []):
        roles = entity.get('roles', [])
        if role_filter and not any(r in roles for r in role_filter):
            continue
        info = {'roles': roles}
        # vCard
        vcard = entity.get('vcardArray', [])
        if len(vcard) >= 2:
            info.update(_extract_vcard(vcard))
        # Remarks (redaction notices etc.)
        for remark in entity.get('remarks', []):
            for desc in remark.get('description', []):
                info.setdefault('remarks', []).append(desc)
        results.append(info)
        # Nested entities
        results.extend(_parse_entities(entity.get('entities', []), role_filter))
    return results


class WhoisLookup:
    """Domain WHOIS via RDAP — structured data for any gTLD."""

    def get_info(self, domain):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"WHOIS / RDAP Lookup"+bc.CEND)
        # Strip protocol and path
        domain = re.sub(r'^https?://', '', str(domain).strip()).split('/')[0].lower()
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Querying RDAP for: {}...\n".format(domain)+bc.CEND)

        data = _rdap_domain(domain)

        if not data:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"RDAP query failed.\n"+bc.CEND)
            return
        if data.get('_not_found'):
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Domain not found in RDAP.\n"+bc.CEND)
            return

        def p(label, val):
            if val:
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
                      "{:<18}".format(label)+bc.CEND+str(val))

        # ── Domain basics ──────────────────────────────────────────────────
        p("Domain",       data.get('ldhName', domain).upper())
        p("Handle",       data.get('handle'))

        # Status flags
        statuses = data.get('status', [])
        if statuses:
            p("Status",   ', '.join(statuses))

        # Dates
        for ev in data.get('events', []):
            action = ev.get('eventAction', '')
            date   = ev.get('eventDate', '')[:10]
            if action == 'registration':
                p("Registered",  date)
            elif action == 'expiration':
                p("Expires",     date)
            elif action == 'last changed':
                p("Last Updated",date)

        # Nameservers
        ns_list = [ns.get('ldhName', '') for ns in data.get('nameservers', []) if ns.get('ldhName')]
        if ns_list:
            p("Nameservers", ', '.join(ns_list))

        # ── Registrar ─────────────────────────────────────────────────────
        registrars = _parse_entities(data.get('entities', []), role_filter=['registrar'])
        if registrars:
            print()
            print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"-- Registrar --"+bc.CEND)
            r = registrars[0]
            p("Name",         r.get('name'))
            p("Organization", r.get('org'))
            for em in r.get('emails', []):
                p("Email",    em)

        # ── Registrant / Admin / Tech ─────────────────────────────────────
        for role in ['registrant', 'administrative', 'technical']:
            contacts = _parse_entities(data.get('entities', []), role_filter=[role])
            if contacts:
                c = contacts[0]
                has_data = any(c.get(k) for k in ['name', 'org', 'emails', 'address', 'phones'])
                if has_data:
                    print()
                    print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+
                          "-- {} --".format(role.capitalize())+bc.CEND)
                    p("Name",         c.get('name'))
                    p("Organization", c.get('org'))
                    p("Address",      c.get('address'))
                    for em in c.get('emails', []):
                        p("Email",    em)
                    for ph in c.get('phones', []):
                        p("Phone",    ph)
                    # Privacy / redaction notices
                    for rem in c.get('remarks', [])[:2]:
                        print("  ["+bc.CYLW+"i"+bc.CEND+"] "+bc.CYLW+str(rem)+bc.CEND)

        # ── RDAP conformance ──────────────────────────────────────────────
        rdap_url = data.get('links', [{}])[0].get('href', '')
        if rdap_url:
            p("RDAP URL",    rdap_url)

        print()
        try:
            bi.outdata['whois'] = data
        except AttributeError:
            pass
