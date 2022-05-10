# Apple VPN .mobileconfig Profile Generator

This repo provides an Apple VPN profile generator based on Python [`plistlib` library](https://docs.python.org/3.8/library/plistlib.html) and follows the Apple Configurator security standards.

## Requirements

- iOS or iPadOS device
- Python 3
- Certbot (optional, for digitally signed profile)

## Install Instructions

The current VPN profile will allow the device automatically connect to an Unifi VPN server when the WiFi SSID does not match a specific value, using the L2TP protocol and a pre-shared key. If the WiFi SSID match, the device will disconnect from VPN server.

Once the profile generated, you can AirDrop or email it to iOS or iPadOS device.

Configurable Python variables:

- `self.address` - Unifi public IP address, automatically retrieved
- `self.name` - Payload display name, default `vpn.domain.com`
- `self.organization` - Payload organization, default `My Company`

Required Python arguments:

- Pre-shared secret key
- WiFi SSID
- Account username

```sh
$ python3 -B vpn.py --help
usage: vpn.py [-h] -k KEY -s SSID -u USERNAME

Generate an Apple VPN profile.

optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     Pre-shared Secret Key
  -s SSID, --ssid SSID  WiFi SSID
  -u USERNAME, --username USERNAME
                        Account Username
```

### Usage Example

Generate the `vpn.mobileconfig` profile. Example for Debian 11 bullseye:

```sh
sudo -i
python3 -B vpn.py -k 'LXJHTs56tmzS8PRN9SNhw6Y5EvkWsPHP' -s MySSID -u floren
ls -lah vpn.mobileconfig
-rw-r--r-- 1 root root 2.3K May  8 22:09 vpn.mobileconfig
```

To sign and encrypt the profile, install the required packages to generate a set of LetsEncrypt certificates:

```sh
apt -y install certbot python3-certbot-dns-cloudflare
```

Generate a [Cloudflare API token](https://developers.cloudflare.com/api/tokens/create/) and insert it into credentials `cloudflare.ini` file:

```sh
cat 'dns_cloudflare_api_token = InsertYourTokenHere' > /etc/letsencrypt/cloudflare.ini
chmod 0600 /etc/letsencrypt/cloudflare.ini
```

Generate the LetsEncrypt wildcard certificate:

```sh
certbot certonly --dns-cloudflare \
    --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
    --domains domain.com,*.domain.com --preferred-challenges dns
```

Sign and encrypt the `signed.mobileconfig` profile:

```sh
openssl smime -sign -nodetach -outform der \
    -signer /etc/letsencrypt/live/domain.com/fullchain.pem \
    -inkey /etc/letsencrypt/live/domain.com/privkey.pem \
    -certfile /etc/letsencrypt/live/domain.com/chain.pem  \
    -in vpn.mobileconfig -out signed.mobileconfig
ls -lah signed.mobileconfig
-rw-r--r-- 1 root root 6.9K May  8 22:10 signed.mobileconfig
```
