import json
import requests
import logging
from requests.exceptions import HTTPError
from common import X_SONOS_API_KEY, INFO_URL
import os
import imp
from retry import retry
import datetime
from twisted.internet import task
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
restLogger = logging.getLogger("Muse-REST")
restLogger.setLevel(logging.INFO)

OAUTH_USER = os.getenv('OAUTH_USER')
OAUTH_PW = os.getenv('OAUTH_PW')
BASE_URL = "{}://{}:{}/api/v{}{}"


class BaseRestClient(object):
    def __init__(self, ip, hhid=None, uuid=None, apiKey=None, apiVersion="1",
                 port=None, secureOverride=None):
        """
        Initialize values
        :param ip:
        :param hhid: player's household id
        :param uuid: player's raw udn
        :param apiKey:
        :param apiVersion: muse api version to use
        :param port: custom port to connect to on the dut
        :param secureOverride: protocol string override "http"/"https"
        """
        super(BaseRestClient, self).__init__()
        if not ip:
            raise ValueError('Please supply a valid ip address')

        self._ip = ip
        self._hhid = hhid
        self._uuid = uuid
        self.logger = restLogger
        self._apiVersion = str(apiVersion)
        self._deviceApiVersion = None
        self._deviceMinApiVersion = None
        self._deviceInfo = None
        self.portOverride = port
        self.protocolOverride = secureOverride
        self._apiKey = X_SONOS_API_KEY if apiKey is None else apiKey

        self.tokenTTL = None
        self.hhConfigToken = None
        self.hhConfigAdminToken = None
        self.userId = None
        if OAUTH_USER is not None and OAUTH_PW is not None:
            # Only attempt to fetch oauth tokens if the OAUTH creds are in the environment
            self.updateOauthTokens()
            # Create a twisted task to re-fetch the oauth tokens 5 minutes before they expire
            # Current understanding is that non-PROD tokens have 1 hour lifetimes. PROD is 24 hours.
            t = task.LoopingCall(self.updateOauthTokens)
            t.start(interval=self.tokenTTL-300, now=False)

        # All v2 commands require a token. Ones that don't have a defined scope, use this fake one for now
        self.hhFakeToken = "FAKE-TOKEN"

        # Try to populate all the target ids
        if not hhid or not uuid:
            self._gid = self.getGroupId()

    @property
    def ip(self):
        """
        Return the IP address of the associated zone player
        """
        return self._ip

    @property
    def api_version(self):
        """
        Return the API version of the associated player
        """
        return self._apiVersion

    @property
    def api_key(self):
        """
        Return the API key
        """
        return self._apiKey

    @property
    def hhid(self):
        """
        Return the householdId of the associated zone player
        """
        return self._hhid

    @property
    def uuid(self):
        """
        Return the playerId of the associated zone player
        """
        return self._uuid

    @property
    def deviceApiVerison(self):
        """
        Return the device.apiVersion of the associated zone player
        :return:
        """
        return self._deviceApiVersion

    @property
    def deviceMinApiVersion(self):
        """
        Return the device.minApiVersion of the associated zone player
        :return:
        """
        return self._deviceMinApiVersion

    @property
    def deviceInfo(self):
        """
        Return the info of the associated zone player
        :return:
        """
        return self._deviceInfo

    @property
    def groupId(self):
        """
        Return the groupId of the associated zone player
        """
        return self._gid

    def hitRestEndpoint(self, cmd_url, reqMethod="GET", apiKey=None, oauthToken=None, params=None,
                        reqHeaders=None, reqJson=None, check=True, send=True, requestObject=None,
                        isSecure=True, overrideUrl=None, reqData=None):
        """
        Helper for Sonos muse REST calls

        :param cmd_url: command path url
        :param reqMethod: GET/PUT/etc
        :param apiKey: sonos api key
        :param oauthToken: oauth token
        :param params:
        :param reqHeaders:
        :param reqJson:
        :param check: If True, the command will assert a 200 response, then parse the body as json
        :param send: If False, return the requests.Request object instead of actually sending it
        :param requestObject: a previously created unprepared requests.Request object
        :param reqData: freeform data to provide in request body
        :param isSecure: Determine which transport/port to use
        :param overrideUrl: Blindly use this string as the request url
        :return: depending on if check is set, either the raw response or the parse JSON body
        """
        restPort = self.getPort(isSecure)
        transportType = self.getProtocol(isSecure)
        if overrideUrl is not None:
            url = overrideUrl
        else:
            url = BASE_URL.format(transportType, self._ip, restPort, self._apiVersion, cmd_url)

        if reqHeaders is None:
            reqHeaders = {}

        if apiKey is None:
            # Muse v1 commands all require an apiKey
            if self._apiVersion == "1":
                reqHeaders["X-Sonos-Api-Key"] = self._apiKey
        else:
            reqHeaders["X-Sonos-Api-Key"] = apiKey

        if oauthToken is None:
            # Muse v2 commands all require a token
            if self._apiVersion == "2":
                reqHeaders["Authorization"] = 'Bearer {}'.format(self.hhConfigToken)
        else:
            reqHeaders["Authorization"] = 'Bearer {}'.format(oauthToken)

        # Player does not handle empty dict in the body correctly
        if not reqJson:
            reqJson = None

        if not send:
            return requests.Request(reqMethod, url, params=params, headers=reqHeaders,
                                    json=reqJson, data=reqData)
        elif requestObject is not None:
            req = requestObject.prepare()
        else:
            req = requests.Request(reqMethod, url, params=params, headers=reqHeaders,
                                   json=reqJson, data=reqData).prepare()

        restLogger.info("<{}> REST Request:\n\t{} {}\n\tHeaders: {}\n\tBody: {}".format(
            datetime.datetime.now().ctime(), req.method, req.url, req.headers, getattr(req, "body", None)))

        with requests.Session() as s:
            resp = s.send(req, verify=False)

            # Try to format assumed json resp content; fall back to bare value if error
            try:
                respText = json.dumps(json.loads(resp.text.encode('utf-8')), indent=4)
            except Exception:
                respText = resp.text

            restLogger.info("<{}> REST Response:\n\tResponse status: {}\n\tResponse content: \n{}".format(
                datetime.datetime.now().ctime(), resp.status_code, respText))
            if check:
                try:
                    resp.raise_for_status()
                except HTTPError as e:
                    # Add additional logging for HTTPErrors
                    raise type(e)(e.message + "\nResp text: {}".format(resp.text))
                except:
                    # Just re-raise for all other exceptions
                    raise
                else:
                    return json.loads(resp.content)
            else:
                return resp

    def getPlayerInfo(self):
        """
        Get the player info parsed json from the Muse getInfo command
        :return:
        """
        # try info.getInfo first
        try:
            return self.hitRestEndpoint(INFO_URL)
        except:
            pass

        try:
            return self.hitRestEndpoint(cmd_url=None, overrideUrl="http://{}:1400/info".format(self._ip))
        except:
            raise

        # assert False, "Failed to fetch :1400/info and /info/getInfo muse endpoint from <{}>".format(self._ip)

    @retry(Exception, tries=6, delay=10)
    def getGroupId(self):
        """
        Get the player's group id from the /info endpoint
        :return:
        """
        # Wait until the householdId is in the right format
        self._deviceInfo = self.getPlayerInfo()

        if "capabilities" in self.getPlayerInfo()["device"] and "PLAYBACK" in self.getPlayerInfo()["device"]["capabilities"]:
            assert len(self._deviceInfo["householdId"].split(".")) == 2, \
                "Playback device at <{}> has hhid <{}>, not in expected format <Sonos_[household].[location]>".format(
                    self._ip, self._deviceInfo["householdId"])

        # opportunistically update all the internal ids
        self._hhid = self.deviceInfo["householdId"]
        self._uuid = self.deviceInfo["playerId"]
        self._gid = self.deviceInfo["groupId"]
        self._deviceApiVersion = self.deviceInfo["device"]["apiVersion"]
        self._deviceMinApiVersion = self.deviceInfo["device"]["minApiVersion"]

        return self.deviceInfo["groupId"]

    def getPort(self, isSecure=True):
        if self.portOverride is not None:
            return self.portOverride
        else:
            return 1443 if isSecure else 1400

    def getProtocol(self, isSecure=True):
        if self.protocolOverride is not None:
            return self.protocolOverride
        else:
            return "https" if isSecure else "http"

    def updateOauthTokens(self, username=OAUTH_USER, password=OAUTH_PW, useV4=False):
        """
        Update the class's internal tokens with the provided username/password.
        By default, use the values set in the env.
        :param username:
        :param password:
        :param useV4:
        :return:
        """
        try:
            imp.find_module("Scopes")
            imp.find_module("OAuth")
        except ImportError:
            from common import Scopes, OAuth

        for scopeString in (Scopes.AS_HH_CONFIG.string, Scopes.AS_HH_CONFIG_ADMIN.string):
            tokenObj = OAuth.get_oauth_token(scope=scopeString, username=username, password=password, use_v4=useV4)
            assert tokenObj is not None, "oauth token request <{}> returned something?".format(tokenObj)
            if scopeString == Scopes.AS_HH_CONFIG.string:
                self.hhConfigToken = tokenObj.token
            elif scopeString == Scopes.AS_HH_CONFIG_ADMIN.string:
                self.hhConfigAdminToken = tokenObj.token
            restLogger.info("<{}>: Requesting <{}> scoped token. TTL is <{}>".format(datetime.datetime.now().ctime(),
                                                                                     scopeString, tokenObj.ttl))
        self.tokenTTL = tokenObj.ttl
        self.userId = tokenObj.owner
        
