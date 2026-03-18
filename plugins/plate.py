from __future__ import absolute_import, print_function
#
# License plate lookup — faxvin.com for plate→VIN, NHTSA free API for VIN decode
# NHTSA API: https://vpic.nhtsa.dot.gov/api/ (US Government, free, no key needed)
#
import re
import requests
from plugins.base import PageGrabber
from plugins.colors import BodyColors as bc

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

NHTSA_URL = 'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{}?format=json'

# NHTSA fields we care about
NHTSA_FIELDS = [
    ('Make',            'Make'),
    ('Model',           'Model'),
    ('Model Year',      'ModelYear'),
    ('Body Class',      'BodyClass'),
    ('Vehicle Type',    'VehicleType'),
    ('Drive Type',      'DriveType'),
    ('Fuel Type',       'FuelTypePrimary'),
    ('Engine Size',     'DisplacementL'),
    ('Cylinders',       'EngineCylinders'),
    ('Engine HP',       'EngineHP'),
    ('Transmission',    'TransmissionStyle'),
    ('Doors',           'Doors'),
    ('Seats',           'SeatRows'),
    ('Series',          'Series'),
    ('Trim',            'Trim'),
    ('Plant Country',   'PlantCountry'),
    ('Manufacturer',    'Manufacturer'),
]

US_STATES = [
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
    'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
    'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
    'TX','UT','VT','VA','WA','WV','WI','WY','DC',
]


def _decode_vin(vin):
    """Decode a VIN using the free NHTSA API. Returns dict of vehicle data."""
    try:
        resp = requests.get(NHTSA_URL.format(vin), timeout=12)
        data = resp.json()
        results = data.get('Results', [{}])[0]
        return results
    except Exception:
        return {}


def _find_vin_in_page(text):
    """Extract a 17-character VIN from raw page text."""
    matches = re.findall(r'\b[A-HJ-NPR-Z0-9]{17}\b', text)
    return matches[0] if matches else None


class VinGrabber(PageGrabber):
    def get_info(self, plate):
        print("["+bc.CPRP+"?"+bc.CEND+"] "+bc.CCYN+"License Plate Lookup"+bc.CEND)

        while True:
            state = input("  ["+bc.CRED+"!"+bc.CEND+"] "+bc.CYLW +
                          "Enter 2-letter state abbreviation [ex: FL, CA, TX]: " +
                          bc.CEND).strip().upper()
            if state in US_STATES:
                break
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"Invalid state. Use 2-letter abbreviation (e.g. FL)."+bc.CEND)

        plate = str(plate).upper().strip()
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Searching plate {} / {}...".format(plate, state)+bc.CEND)

        vin = None

        # --- Attempt 1: faxvin.com ---
        try:
            faxvin_url = 'https://www.faxvin.com/license-plate-lookup/result?plate={}&state={}'.format(plate, state)
            source = self.get_source(faxvin_url)
            if source:
                vin = _find_vin_in_page(source)
                if vin:
                    print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"VIN extracted: "+bc.CEND+vin)
        except Exception:
            pass

        # --- Attempt 2: ask user to supply VIN manually ---
        if not vin:
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW +
                  "Automated VIN lookup unavailable (sites require JavaScript)." + bc.CEND)
            manual = input("  ["+bc.CRED+"?"+bc.CEND+"] "+bc.CYLW +
                           "Enter VIN manually to decode via NHTSA (or press Enter to skip): " +
                           bc.CEND).strip().upper()
            if manual and len(manual) == 17:
                vin = manual
            else:
                print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"No VIN provided. Skipping decode.\n"+bc.CEND)
                return

        # --- Decode VIN via NHTSA free government API ---
        print("  ["+bc.CBLU+"~"+bc.CEND+"] "+bc.CYLW+"Decoding VIN via NHTSA API (free)..."+bc.CEND)
        vehicle = _decode_vin(vin)

        if not vehicle or vehicle.get('ErrorCode', '0') != '0':
            print("  ["+bc.CRED+"X"+bc.CEND+"] "+bc.CYLW+"NHTSA could not decode this VIN.\n"+bc.CEND)
            return

        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"Plate: "+bc.CEND+plate)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"State: "+bc.CEND+state)
        print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"VIN:   "+bc.CEND+vin)

        result = {'plate': plate, 'state': state, 'vin': vin}
        for label, key in NHTSA_FIELDS:
            val = vehicle.get(key, '').strip()
            if val and val != 'Not Applicable':
                print("  ["+bc.CGRN+"+"+bc.CEND+"] "+bc.CRED+"{}: ".format(label)+bc.CEND+val)
                result[label.lower().replace(' ', '_')] = val

        self.info_dict.update(result)
        bi.outdata['plate_lookup'] = self.info_dict
        print()
