from collections import namedtuple
import ssl
import requests
from requests import codes as HTTPStatusCodes
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.packages.urllib3.poolmanager import PoolManager
import logging
import os
from retry import retry

# assert "MITC_ENVIRONMENT" in os.environ, \
#    "$MITC_ENVIRONMENT is not set, please see <IP:1400/testenv> on your ZP for correct value"
# assert "OAUTH_USER" in os.environ, \
#    "$OAUTH_USER is not set, please see <:1400/testenv> on your ZP for correct value"
# assert "OAUTH_PW" in os.environ, \
#    "$OAUTH_PW is not set, please see <:1400/testenv> on your ZP for correct value"

API_KEYS = {
    'prod':     "e0babc90-6e2d-4a72-9b50-3fbda4a2ecbb",
    'test':     "e61bc77c-39cd-4ed0-a5e7-5ad316a0efc5",
    'stage':    "492fc9df-7969-472c-971f-604d3ee8279b",
    'int':      "22da8140-ddc6-4550-9bde-9dccaf652b86",
}

MITC_ENVIRONMENT = os.environ['MITC_ENVIRONMENT'].lower() if 'MITC_ENVIRONMENT' in os.environ else None
if MITC_ENVIRONMENT in API_KEYS:
    X_SONOS_API_KEY = API_KEYS[MITC_ENVIRONMENT]
else:
    X_SONOS_API_KEY = API_KEYS['test']

INFO_URL = "/players/local/info"

MITC_ENVIRONMENT = os.getenv('MITC_ENVIRONMENT')

L7_OVERRIDE_NAME = "O_CLOUD_API_BASE_URL"

L7_TLD = "{}ws.sonos.com".format(
     '' if MITC_ENVIRONMENT == 'prod' else
     '{}.'.format(MITC_ENVIRONMENT))

L7_DEFAULT_HOST = "api.{}".format(L7_TLD)
L7_LECHMERE_HOST = "lechmere-v1.{}".format(L7_TLD)
L7_OAUTH_HOST = "oauth.{}".format(L7_TLD)
L7_REGISTRATION_HOST = "registration.{}".format(L7_TLD)

L7_BASE_DEFAULT_URL = "https://{}".format(L7_DEFAULT_HOST)
L7_BASE_LECHMERE_URL = "https://{}".format(L7_LECHMERE_HOST)
L7_BASE_USER_OAUTH_URL = "https://{}".format(L7_OAUTH_HOST)
L7_BASE_REGISTRATION_URL = "https://{}".format(L7_REGISTRATION_HOST)

VERSION = "v2"
VERISON_V4 = "v4"

L7_OAUTH_EP = "{}/auth/oauth/{}".format(L7_BASE_USER_OAUTH_URL, VERSION)
V4_OAUTH_EP = "{}/oauth/{}".format(L7_BASE_USER_OAUTH_URL, VERISON_V4)
L7_WS_EP = "{}/websocket/v0".format(L7_BASE_LECHMERE_URL)

DEFAULT_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Authorization': ''}
DEFAULT_BODY = 'username={}&password={}&grant_type=password&scope={}'

# URI and request parameters for Secure Registration
INIT_URL_METHOD = '/product/{}/households/{{}}/players'.format(VERSION)
INIT_URL = '{}{}?action=init'.format(L7_BASE_REGISTRATION_URL, INIT_URL_METHOD)
INIT_URL_ACTION = '{}{}?action=complete'.format(L7_BASE_REGISTRATION_URL, INIT_URL_METHOD)
INIT_BODY_FIELDS = ('mac', 'userId')

OAUTH_USER = os.getenv('OAUTH_USER')
OAUTH_PW = os.getenv('OAUTH_PW')

OAuthToken = namedtuple('OAuthToken', 'token ttl owner scope refresh_token type uid luid')

_logger = logging.getLogger('Client Oauth Token')

AuthScope = namedtuple("Scope", "string value role")

ROLE_SERVICE = "ROLE_SERVICE"
ROLE_CONTROLLER = "ROLE_CONTROLLER"


class Scopes(object):
    # Add player is a controller scope that has the same value
    # as hh_config
    AS_ADD_PLAYER = AuthScope("add-player", 0x00000001, ROLE_CONTROLLER)
    AS_HH_CONFIG = AuthScope("hh-config", 0x000000001, ROLE_SERVICE)
    AS_HH_CONFIG_ADMIN = AuthScope("hh-config-admin", 0x000000002, ROLE_SERVICE)

    _scopes = (AS_ADD_PLAYER,
               AS_HH_CONFIG,
               AS_HH_CONFIG_ADMIN)

    def __iter__(self):
        return (i for i in self._scopes)

    @classmethod
    def from_string(cls, scope):
        for s in cls._scopes:
            if s.string == scope:
                return s
        assert False, \
            "Could not figure out which scope({}) maps to string: <{}> ".format(cls._scopes,
                                                                                scope)


AUTOMATION_OAUTH_SCOPE = Scopes.AS_ADD_PLAYER.string
OAUTH_SCOPE = os.getenv('OAUTH_SCOPE') or AUTOMATION_OAUTH_SCOPE

# Added from SWPBL-133337
# Base64 encoded client_key:secret values
# Currently, the keys for both roles have "hh-config,hh-config-admin,add-player,partner-auth" enabled
# Once SWPBL-133334 is implemented, the keys for each role has have their scopes downsized to their appropriate products
MITC_AUTH_KEY_MATRIX = {"prod": {ROLE_SERVICE: "NDg3ODlmMmMtZWZjYy00MTQxLTkzMTQtZTRlMDNmNmY0OGMxOjY3M2Y3NjhhLTg2MzctNGQ5Yi1hODJmLWJmNDYzMWYyM2Q1Mw==",
                                 ROLE_CONTROLLER: "MDA5YmM2NDItMGU1YS00ZDAwLWI0ZjAtM2IwNGZjYzI2YjliOjg5NWZhMTIyLTAxNDEtNGVmMy05MDZlLThkNDc3YmE1YjdhMA=="},
                        "test": {ROLE_SERVICE: "MTg0ZjEyMGEtZjg2OS00MDk5LTk3NDMtNzIwMTRjMjc4NTVkOjQyZWQ0NTViLTNiMWUtNGI3MS1iMWJhLWE4YzhkMWYxYWYwMw==",
                                 ROLE_CONTROLLER: "MDQ4NjkzMjQtMzU5Yi00MjdkLTg2ZGYtYjM5NGE1MDk3ZmQ3OjVkNTY1M2U4LWNmZWQtNDRmYy1iZjJjLTA0M2NmNGQwN2MwMA=="},
                        "stage": {ROLE_SERVICE: "ZTY5YWYyYzAtNmMwNy00Mjc3LTg2MDEtNWZhMmQ4NWRiZmUyOjg1MWFlOWZmLWEyYjUtNGYyNS1hMTA0LTI2N2U2ZTg4MDk5OQ==",
                                  ROLE_CONTROLLER: "OTA3MWE0YmEtNGRiZS00Mzg4LTlhMGItMzAyMzAxMGRmMjU2OjdkN2JkZjFkLWNjNGEtNGE5Ny04MzYyLTBmNjk0NjJhODJiZg=="},
                        "int": {ROLE_SERVICE: "ZGRlMDZjZTMtMzVlZi00YWU3LWIxYzItYmY3NDhjYWZhYzg4OjNlZTgxMDhhLWE2OWMtNGQwYy1hMGRkLWJkNDVkZTE1YTJmMA==",
                                ROLE_CONTROLLER: "YWY0YTdhZjAtMjY0Zi00ZTc1LThhNmQtNjVhZDdiMjgyY2RiOjRhOTgwNWE5LTIxOGUtNDFkZi1hZjI4LTkxMGM0NDEwZWVkNg=="}
                        }

MITC_AUTH_KEY_MATRIX_V4 = {"prod": {ROLE_SERVICE: None,
                                 ROLE_CONTROLLER: None},
                             "test": {ROLE_SERVICE: "YTM0YjU5YTItZjJlMS00OGRiLThlMWItNzliOWVlYWZiMDQ5OjFjODc0MDg4LWFkNjEtNDAxMy04MzFhLWIwYWM4ZGYyOTJmOQ==",
                                      ROLE_CONTROLLER: "YTM0YjU5YTItZjJlMS00OGRiLThlMWItNzliOWVlYWZiMDQ5OjFjODc0MDg4LWFkNjEtNDAxMy04MzFhLWIwYWM4ZGYyOTJmOQ=="},
                             "stage": {ROLE_SERVICE: "Yzc4OWQ4NmMtN2Y0NS00MmJmLWFiNDgtNWI3MWMzODIxMjYyOjAzYzQwNGU4LTU0N2EtNDY3NS1hYjE1LTU4NTkwZGVkYTYyYQ==",
                                       ROLE_CONTROLLER: "Yzc4OWQ4NmMtN2Y0NS00MmJmLWFiNDgtNWI3MWMzODIxMjYyOjAzYzQwNGU4LTU0N2EtNDY3NS1hYjE1LTU4NTkwZGVkYTYyYQ=="},
                             "int": {ROLE_SERVICE: "NmI2NzNkNGItMTQzNS00YTkyLWI2MDUtNGY5OTZjZmY2ODg5OjI5OTJkNmVmLTYxN2QtNDQ1MC04ODFkLWQ4ZjZjNGE2ZmFjOA==",
                                     ROLE_CONTROLLER: "NmI2NzNkNGItMTQzNS00YTkyLWI2MDUtNGY5OTZjZmY2ODg5OjI5OTJkNmVmLTYxN2QtNDQ1MC04ODFkLWQ4ZjZjNGE2ZmFjOA=="}
                             }


class ForceTLSAdapter(HTTPAdapter):
    """
    Require TLS for the connection
    """
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1,
        )


class OAuth(object):
    """
    Class for requests to OAuth server
    """

    @classmethod
    def get_tls_session(cls):
        s = requests.Session()
        s.mount('https://', ForceTLSAdapter())
        return s

    @classmethod
    @retry(Exception, tries=5, delay=10)
    def get_oauth_token(cls, username=OAUTH_USER, password=OAUTH_PW,
                        scope=OAUTH_SCOPE, force_tls=True, use_v4=False):
        """
        Get an OAuth token for username/password.

        :param str scope: desired token scope
        :param str username: Username for SonosID (ex. bob@sonos.com)
        :param str password: Password for SonosID
        :param bool force_tls: Force tls for connection
        :param bool use_v4: Use the v4 endpoint which will support returning okta tokens
        :return: Tuple with (access_token, ttl)
        :rtype: :class:`OAuthToken`

        :raises: :class:~`requests.exceptions.HTTPError` on 4xx or 5xx response
        """
        session = cls.get_tls_session() if force_tls else requests

        # Get the correct auth key based on the role/env/token provider and populate it into DEFAULT_HEADERS
        scope_role = Scopes.from_string(scope).role
        if use_v4:
            url = "{}/{}".format(V4_OAUTH_EP, "token")
            basic_key = MITC_AUTH_KEY_MATRIX_V4[MITC_ENVIRONMENT][scope_role]
        else:
            url = "{}/{}".format(L7_OAUTH_EP, "token")
            basic_key = MITC_AUTH_KEY_MATRIX[MITC_ENVIRONMENT][scope_role]
        assert basic_key is not None, "Auth key for {} is None".format(MITC_ENVIRONMENT)
        DEFAULT_HEADERS["Authorization"] = "Basic {}".format(basic_key)

        if username is None:
            raise EnvironmentError("Could not find a secure registration account. "
                                   "Please check the test environment for an OAUTH_USER and OAUTH_PW "
                                   "environment variable.")

        res = session.post(url,
                           headers=DEFAULT_HEADERS, verify=False,
                           data=DEFAULT_BODY.format(username, password, scope))

        # Raise for status if 4xx or 5xx response
        try:
            res.raise_for_status()
        except RequestException as e:
            # Logging for 401
            if e.response.status_code == HTTPStatusCodes.UNAUTHORIZED: # @UndefinedVariable
                _logger.critical("Got {} response code from {} trying to get OAuth token, "
                    "credentials may be bad (specify with environment variables"
                    " OAUTH_USER='example@sonos.com' and OAUTH_PW='password')".
                    format(HTTPStatusCodes.UNAUTHORIZED, url)) # @UndefinedVariable
                _logger.critical("Request -- url:<{}>, headers:<{}>, body:<{}>".
                    format(e.request.url, e.request.headers, e.request.body))
                _logger.critical("Response -- url:<{}>, headers:<{}>, body:<{}>".
                    format(e.response.url, e.response.headers, e.response.text))
            raise

        rjson = res.json()

        return OAuthToken(token=rjson.get('access_token'),
                          ttl=rjson.get('expires_in'),
                          owner=rjson.get('resource_owner'),
                          scope=rjson.get('scope'),
                          refresh_token=rjson.get('refresh_token'),
                          type=rjson.get('token_type'),
                          uid=rjson.get('uid'),
                          luid=rjson.get('luid'))
