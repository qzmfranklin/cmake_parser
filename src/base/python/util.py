'''Miscellaneous utilities.
'''

import pathlib
import re
import requests

THIS_DIR = pathlib.Path(__file__).resolve().parent
__PATH_REGEX__ = re.compile(r'[^/][a-zA-Z0-9_/]+\.py')


def path_to_module(path):
    '''Convert a path to a string suitable for __import__.

    :param path: A relative path.
    :type path: str or pathlib.Path

    :raises: ValueError if the path cannot be converted to a valid module.
    '''
    if not __PATH_REGEX__.match(str(path)):
        raise ValueError('Invalid python module path.', path)
    return str(path)[:-3].replace('/', '.')


def get_workspace():
    '''Get the root directory of this repository.

    This is the same as the directory containing the bazel WORKSPACE file.

    :return: The path to the root directory.
    :rtype: pathlib.Path.
    '''
    curr_dir = THIS_DIR
    # pylint: disable=no-member
    while not (curr_dir.parent / 'WORKSPACE').is_file():
        curr_dir = curr_dir.parent
    if curr_dir == '/':
        raise RuntimeError(
            'Cannot find WORKSPACE by reverse traversing %s' % THIS_DIR
        )
    return curr_dir.parent


def get_country_code(ip_addr=None):
    '''Get the uppercase two-letter country code for the ip address.

    This method requires HTTP connectivity to the following domain:
            www.ip-api.com

    :param ip_addr: The ip address to query the country code for.  The default
        value, None, causes the method to issue the query using the ip address
        seen by the www.ip-api.com domain.  Depending on the networking path,
        e.g., with VPN, it may or may not accurately represent your true
        location.
    :type ip_addr: str or None.

    :raises: (TBD) Some exception indicating failure of connectivity if no
        network connectivity to www.ip-api.com is available.
    '''
    domain_url = 'http://www.ip-api.com/json'
    if ip_addr:
        url = '/'.join([domain_url, ip_addr])
    else:
        url = domain_url
    r = requests.get(url)  # pylint: disable=invalid-name
    r.raise_for_status()
    return r.json()['countryCode']
