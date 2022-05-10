#!/usr/bin/env python3

from argparse import ArgumentError, ArgumentParser
from collections.abc import Mapping
from plistlib import dump, FMT_XML
from urllib.request import urlopen
from uuid import uuid4

class VpnProfile:
    """
    VpnProfile generates the vpn.mobileconfig file.
    """
    def __init__(self, key, ssid, username, directory = '.'):
        """
        Constructs a new 'VpnProfile' object.
        :param key: Pre-shared secret key
        :param ssid: WiFi ssid
        :param username: Account username
        :param directory: Path of the build directory
        :return: Nothing
        """
        self.address = urlopen('https://checkip.amazonaws.com').read().decode('utf8').strip()
        self.directory = str(directory)
        self.name = 'vpn.domain.com'
        self.organization = 'My Company'
        self.key = str(key)
        self.ssid = str(ssid)
        self.username = str(username)
        self.uuid = str(uuid4())
        self.settings = {
            'PayloadContent': [
                {
                    'IPSec': {
                        'AuthenticationMethod': 'SharedSecret',
                        'LocalIdentifierType': 'KeyID',
                        'SharedSecret': bytes(self.key, encoding='utf8')
                    },
                    'IPv4': {
                        'OverridePrimary': 1
                    },
                    'OnDemandEnabled': 1,
                    'OnDemandRules': [
                        {
                            'Action': 'Disconnect',
                            'InterfaceTypeMatch': 'WiFi',
                            'SSIDMatch': [
                                self.ssid
                            ]
                        },
                        {
                            'Action': 'Connect'
                        }
                    ],
                    'PayloadDescription': '{0} VPN profile configuration.'.format(self.organization),
                    'PayloadDisplayName': self.name,
                    'PayloadIdentifier': 'com.apple.vpn.managed.{0}'.format(self.uuid),
                    'PayloadOrganization': self.organization,
                    'PayloadType': 'com.apple.vpn.managed',
                    'PayloadUUID': self.uuid,
                    'PayloadVersion': 1,
                    'PPP': {
                        'AuthName': self.username,
                        'CommRemoteAddress': self.address
                    },
                    'UserDefinedName': self.name,
                    'VPNType': 'L2TP'
                }
            ],
            'PayloadDisplayName': 'VPN Configuration',
            'PayloadIdentifier': str(uuid4()),
            'PayloadOrganization': self.organization,
            'PayloadRemovalDisallowed': False,
            'PayloadType': 'Configuration',
            'PayloadUUID': str(uuid4()),
            'PayloadVersion': 1
        }


    def write_config(self):
        """
        Generates the VPN configuration file.
        :return: Nothing
        """
        file = '{0}/vpn.mobileconfig'.format(self.directory)
        with open(file, 'wb') as config:
            dump(self.settings, config, fmt=FMT_XML, sort_keys=True)
        print('Configuration created.')


if __name__ == '__main__':
    parser = ArgumentParser(description='Generate an Apple VPN profile.')
    parser.add_argument('-k', '--key', required=True, help='Pre-shared Secret Key')
    parser.add_argument('-s', '--ssid', required=True, help='WiFi SSID')
    parser.add_argument('-u', '--username', required=True, help='Account Username')
    try:
        a = parser.parse_args()
    except ArgumentError:
        parser.print_help()
    else:
        build = VpnProfile(a.key, a.ssid, a.username)
        build.write_config()
