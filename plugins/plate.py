from __future__ import absolute_import, print_function
#
# Vehicle lookup — NHTSA free government API (no key required)
#
# Reality of plate-to-VIN:
#   Every free plate lookup site (faxvin, vindecoderz, etc.) is either:
#     - JavaScript-gated (requires headless browser)
#     - Cloudflare-blocked (403)
#     - Dead (DNS fails / 404)
#   Real plate-to-VIN lookup requires paid DMV API access (carmd, platescanner, etc.)
#   OR the vehicle owner to supply the VIN themselves.
#
# What DOES work (free, no key, instant):
#   NHTSA VIN Decoder  : full specs from any 17-char VIN
#   NHTSA Model Search : all models for a given make + year
#
import re
import requests
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

NHTSA_DECODE_URL = 'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{}?format=json'
NHTSA_MAKES_URL  = 'https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json'
NHTSA_MODELS_URL = 'https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{}/modelyear/{}?format=json'

NHTSA_FIELDS = [
    ('Make',           'Make'),
    ('Model',          'Model'),
    ('Year',           'ModelYear'),
    ('Body Class',     'BodyClass'),
    ('Vehicle Type',   'VehicleType'),
    ('Drive Type',     'DriveType'),
    ('Fuel Type',      'FuelTypePrimary'),
    ('Engine (L)',     'DisplacementL'),
    ('Cylinders',      'EngineCylinders'),
    ('Horsepower',     'EngineHP'),
    ('Transmission',   'TransmissionStyle'),
    ('Doors',          'Doors'),
    ('Seat Rows',      'SeatRows'),
    ('Series',         'Series'),
    ('Trim',           'Trim'),
    ('Manufacturer',   'Manufacturer'),
    ('Plant Country',  'PlantCountry'),
    ('GVWR',           'GVWR'),
    ('Brake System',   'BrakeSystemType'),
    ('Steering',       'SteeringType'),
    ('Wheelbase (in)', 'WheelBaseShort'),
    ('ABS',            'ABS'),
    ('Airbags',        'AirBagLocFront'),
    ('NCAP Safety',    'RearAutomaticEmergencyBraking'),
    ('Error Code',     'ErrorCode'),
    ('Error Text',     'ErrorText'),
]

US_STATES = [
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
    'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
    'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
    'TX','UT','VT','VA','WA','WV','WI','WY','DC',
]

VIN_RE = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')


def _decode_vin(vin):
    """Decode a VIN using the NHTSA free API. Returns result dict."""
    try:
        resp = requests.get(NHTSA_DECODE_URL.format(vin), timeout=12)
        data = resp.json()
        return data.get('Results', [{}])[0]
    except Exception:
        return {}


def _print_vehicle(vehicle, plate=None, state=None, vin=None):
    """Print decoded vehicle fields."""
    if plate:
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Plate:  "+bc.CEND+plate)
    if state:
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"State:  "+bc.CEND+state)
    if vin:
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"VIN:    "+bc.CEND+vin)
    print()

    result = {}
    for label, key in NHTSA_FIELDS:
        val = vehicle.get(key, '').strip()
        if not val or val in ('Not Applicable', '0', ''):
            continue
        # Skip error fields unless there's actually an error
        if key == 'ErrorCode' and val == '0':
            continue
        if key == 'ErrorText' and 'PASS' in val.upper():
            continue
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
              "{:<16}".format(label)+bc.CEND+val)
        result[label.lower().replace(' ', '_')] = val

    return result


class VinGrabber:

    def __init__(self):
        self.info_dict = {}

    # ── Direct VIN decode ──────────────────────────────────────────────────────

    def decode_vin(self, vin=None):
        """Decode a VIN directly — prompts for VIN if not supplied."""
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"VIN Decoder (NHTSA)"+bc.CEND)

        if not vin:
            vin = input("  ["+bc.CRED+"!"+bc.CEND+"] "+bc.CYLW +
                        "Enter 17-character VIN: "+bc.CEND).strip().upper()

        if not VIN_RE.match(vin):
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "Invalid VIN format. Must be 17 characters (A-H, J-N, P-Z, 0-9).\n"+bc.CEND)
            return

        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Querying NHTSA API..."+bc.CEND)
        vehicle = _decode_vin(vin)

        if not vehicle:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"NHTSA returned no data.\n"+bc.CEND)
            return

        result = _print_vehicle(vehicle, vin=vin)
        if not result:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"NHTSA could not decode this VIN.\n"+bc.CEND)
            return

        self.info_dict.update({'vin': vin, **result})
        try:
            bi.outdata['plate_lookup'] = self.info_dict
        except AttributeError:
            pass
        print()

    # ── Plate + manual VIN fallback ───────────────────────────────────────────

    def get_info(self, plate):
        """Plate lookup: automated sources are all blocked, falls back to manual VIN."""
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"License Plate Lookup"+bc.CEND)

        while True:
            state = input("  ["+bc.CRED+"!"+bc.CEND+"] "+bc.CYLW +
                          "State abbreviation [ex: FL, CA, TX]: "+bc.CEND).strip().upper()
            if state in US_STATES:
                break
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Invalid state."+bc.CEND)

        plate = str(plate).upper().strip()
        print()
        print("  ["+bc.CYLW+"!"+bc.CEND+"] "+bc.CRED+"Plate: "+bc.CEND+plate+" / "+state)
        print()
        print("  ["+bc.CBLU+"i"+bc.CEND+"] "+bc.CYLW +
              "Plate-to-VIN requires paid DMV API access (carmd.com, platescanner.com)"+bc.CEND)
        print("  ["+bc.CBLU+"i"+bc.CEND+"] "+bc.CYLW +
              "All free plate lookup sites are JavaScript-gated or Cloudflare-blocked."+bc.CEND)
        print("  ["+bc.CBLU+"i"+bc.CEND+"] "+bc.CYLW +
              "If you have the VIN (found on dashboard, door jamb, or title), enter it below."+bc.CEND)
        print()

        vin = input("  ["+bc.CRED+"?"+bc.CEND+"] "+bc.CYLW +
                    "Enter VIN to decode (or press Enter to cancel): "+bc.CEND).strip().upper()

        if not vin:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No VIN entered.\n"+bc.CEND)
            return

        if not VIN_RE.match(vin):
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "Invalid VIN — must be exactly 17 characters.\n"+bc.CEND)
            return

        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Decoding via NHTSA API..."+bc.CEND)
        vehicle = _decode_vin(vin)

        if not vehicle:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"NHTSA returned no data.\n"+bc.CEND)
            return

        result = _print_vehicle(vehicle, plate=plate, state=state, vin=vin)
        self.info_dict.update({'plate': plate, 'state': state, 'vin': vin, **result})
        try:
            bi.outdata['plate_lookup'] = self.info_dict
        except AttributeError:
            pass
        print()

    # ── Model search by make + year ───────────────────────────────────────────

    def search_models(self):
        """List all NHTSA-registered models for a given make and year."""
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"Vehicle Model Search (NHTSA)"+bc.CEND)

        make = input("  ["+bc.CRED+"!"+bc.CEND+"] "+bc.CYLW +
                     "Enter vehicle make (e.g. Ford, Toyota, BMW): "+bc.CEND).strip()
        year = input("  ["+bc.CRED+"!"+bc.CEND+"] "+bc.CYLW +
                     "Enter model year (e.g. 2021): "+bc.CEND).strip()

        if not make or not year.isdigit():
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Invalid input.\n"+bc.CEND)
            return

        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW +
              "Querying NHTSA for {} {}...".format(year, make)+bc.CEND)

        try:
            resp = requests.get(
                NHTSA_MODELS_URL.format(requests.utils.quote(make), year),
                timeout=10
            )
            data = resp.json()
            models = data.get('Results', [])
        except Exception as e:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Request failed: {}\n".format(e)+bc.CEND)
            return

        if not models:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "No models found for {} {}.\n".format(year, make)+bc.CEND)
            return

        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED +
              "Found {} model(s) for {} {}:\n".format(len(models), year, make.upper())+bc.CEND)
        for m in models:
            name = m.get('Model_Name', '')
            mid  = m.get('Model_ID', '')
            print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CYLW+name+bc.CEND +
                  (bc.CBLU+" (ID: {})".format(mid)+bc.CEND if mid else ''))

        try:
            bi.outdata['model_search'] = {'make': make, 'year': year, 'models': models}
        except AttributeError:
            pass
        print()
