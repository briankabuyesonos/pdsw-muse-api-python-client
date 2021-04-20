**PYTHON MUSE CLIENT**

**-------------------------------------------------------- ABOUT ---------------------------------------------------------**

The muse client is written for the latest release of python2.7. 

Originally intended to by tightly coupled with our automation framework, this package is now completely standalone.

It supports muse v1 and v2 over both REST and websocket interfaces to the player.

For more information regarding muse, please see: https://github.com/Sonos-Inc/pdsw-muse-api

The muse client generator uses mustache templates to create the muse rest and websocket clients from the muse IDL xmls.
Mustache templates are divided into two parts:

    * The Mustache template (muse_platform_api/mustache/*.mustache) - This is where all client output code and
       formatting should go.
    * The view class (muse_platform_api/mustache/muse_client_view.py) - This reads the xmls and formats the information
       into a python object, corresponding to the structure of the mustache template.

Each mustache file has a corresponding Python class, with the same name in CamelCase. ie, the "muse_rest_client.mustache"
template implicitly points to the MuseRestClient class.

More information about mustache templates can be found at:

    * https://confluence.sonos.com/display/PDSW/Mustache+Templates+Cheat+Sheet
    * https://mustache.github.io/mustache.5.html
    * https://github.com/defunkt/pystache

**---------------------------------------------- HOW TO INSTALL THE PACKAGE -----------------------------------------------**

The sonos-museclient package is generated and saved as an artifact each time the "Generate automation muse client" 
action is run:

https://github.com/Sonos-Inc/pdsw-muse-api/actions?query=workflow%3A%22Generate+automation+muse+clients%22

It is also saved as a release asset when a new tag is created:

https://github.com/Sonos-Inc/pdsw-muse-api/releases

To generate and install the package locally (Linux instructions):

    1. Checkout the "pdsw-muse-api" repo (Mainline is fine unless you need a specific branch): 
       https://github.com/Sonos-Inc/pdsw-muse-api
    2. cd into the "libraries/python/muse_platform_api" dir
    3. Make sure the following pip modules are installed: 
       pip install -r generator_requirements.txt
    4. Run the generator script to create the client files: 
       "python muse_client_generator.py --api_source ../../../ --api_version <SOME_VERSION_STRING>"
        a. "api_version" is used to define the pip package version. 
        b. Its usually latest tag from https://github.com/Sonos-Inc/pdsw-muse-api/releases but can be any arbitary string.
    5. To package everything up, the "setup_template.py" should be updated with whatever was used for <SOME_VERSION_STRING> from the previous step:
       "sed s/replaceme/<SOME_VERSION_STRING>/ setup_template.py > setup.py"
       a. This package is now ready to be installed locally:
          "pip install ."
    6. (Optional, not usually done by hand) To create the compressed pip module:
       "python setup.py sdist"
        a. The compressed package is located in the "dist" folder. This file can then be uploaded to our pypi repository in artifactory via twine:
           "python -m twine upload -u ARTIFACTORY_USER -p ARTIFACTORY_PASSWORD --repository-url '$PYPI_ADDR' dist/*"


Currently github is not able to directly upload the pip module directly to our internal pypi server.
To get around this, there is a jenkins job that is triggered by webhooks to perform the previously mentioned
package generation and upload:

https://jenkins.sonos.com/main/job/pdsw-muse-api-automation-client/

To install the client from our pypi server:

```
pip install --extra-index-url=https://sa-plx-auto-ro:AKCp5dKswLLW5cNtcZ1mDWJEbNej4712UnAEeqPtteQxS7nJUigsZZ2qMd2kX4PYKsDM5ukdf@artifactory.sonos.com/artifactory/api/pypi/sonos-pypi/simple sonos-museclient
```


**-------------------------------------------------------- USAGE ---------------------------------------------------------**

NOTE: 

Both REST and Websocket clients are able to autopopulate oauth tokens for commands (v1 & v2) that require authentication.

However the following env vars must be set:

    * $MITC_ENVIRONMENT - Set value to "Current test environment: " output from htpp://DEVICE_IP:1400/testenv url
    * $OAUTH_USER - username of the acount the household is registered with
    * $OAUTH_PW - password associated with the $OAUTH_USER
    
    Example:
    export MITC_ENVIRONMENT="test"
    export OAUTH_USER="my.name@sonos.com"
    export OAUTH_PW="strongPassword"


The follow usage examples were captured in ipython. 
If you don't have it, install via "pip install ipython" or "sudo apt install ipython".
Then start it from your terminal: "$ ipython".

**REST client (muse v1)**
```
In [2]: from sonos_museclient.muse_rest_client import MuseRestClient
In [3]: rest_client = MuseRestClient("192.168.1.240")
In [4]: rest_client.info.getInfo()
...
Out[4]: 
{u'device': {u'apiVersion': u'1.24.0-alpha.1+pint-fusion-integ.alpha.63.0-82280',
  u'capabilities': [u'PLAYBACK',
   u'CLOUD',
   u'LINE_IN',
   u'AUDIO_CLIP',
   u'FIXED_VOLUME'],
  u'color': u'White',
  u'hwVersion': u'1.22.1.5-1.1',
  u'id': u'RINCON_949F3EBA4C1801400',
  u'minApiVersion': u'1.1.0',
  u'model': u'S15',
  u'modelDisplayName': u'Connect',
  u'name': u'S15',
  u'serialNumber': u'94-9F-3E-BA-4C-18:8',
  u'softwareVersion': u'63.0-82280-pint-fusion-integ',
  u'swGen': 2},
 u'groupId': u'RINCON_949F3EBA4C1801400:3651079181',
 u'householdId': u'Sonos_QtdkCCeSLTp2OLw9n9QvZcJrUk.YFDqOIeCRZ2sE7eR2x4i',
 u'playerId': u'RINCON_949F3EBA4C1801400',
 u'restUrl': u'https://192.168.1.240:1443/api',
 u'websocketUrl': u'wss://192.168.1.240:1443/websocket/api'}
```

**REST client (muse v2)**
```
In [1]: from sonos_museclient.muse_rest_client_v2 import MuseRestClient as MuseRestClientV2
In [2]: rest_client_v2 = MuseRestClientV2("192.168.1.240")
In [5]: rest_client_v2.info.getInfo()
...
Out[5]: 
{u'device': {u'apiVersion': u'1.24.0-alpha.1+pint-fusion-integ.alpha.63.0-82280',
  u'capabilities': [u'PLAYBACK',
   u'CLOUD',
   u'LINE_IN',
   u'AUDIO_CLIP',
   u'FIXED_VOLUME'],
  u'color': u'White',
  u'hwVersion': u'1.22.1.5-1.1',
  u'id': u'RINCON_949F3EBA4C1801400',
  u'minApiVersion': u'1.1.0',
  u'model': u'S15',
  u'modelDisplayName': u'Connect',
  u'name': u'S15',
  u'serialNumber': u'94-9F-3E-BA-4C-18:8',
  u'softwareVersion': u'63.0-82280-pint-fusion-integ',
  u'swGen': 2},
 u'groupId': u'RINCON_949F3EBA4C1801400:3651079181',
 u'householdId': u'Sonos_QtdkCCeSLTp2OLw9n9QvZcJrUk.YFDqOIeCRZ2sE7eR2x4i',
 u'playerId': u'RINCON_949F3EBA4C1801400',
 u'restUrl': u'https://Sonos-949F3EBA4C18.local:1443/api',
 u'websocketUrl': u'wss://Sonos-949F3EBA4C18.local:1443/websocket/api'}
```

**Websocket client (muse v1)**
```
In [6]: from sonos_museclient.muse_websocket_client import MuseWebsocketClient 
In [7]: ws_client = MuseWebsocketClient("192.168.1.240")
In [8]: ws_client.info.getInfo()
...
INFO:Muse-Websocket:<Thu Oct 29 14:19:46 2020> Sent to 192.168.1.240: 
[
    {
        "playerId": "RINCON_949F3EBA4C1801400", 
        "command": "getInfo", 
        "cmdId": "1", 
        "namespace": "info"
    }, 
    {}
]

INFO:Muse-Websocket:<Thu Oct 29 14:19:46 2020> Received from 192.168.1.240: 
[
    {
        "success": true, 
        "playerId": "RINCON_949F3EBA4C1801400", 
        "namespace": "info", 
        "householdId": "Sonos_QtdkCCeSLTp2OLw9n9QvZcJrUk.YFDqOIeCRZ2sE7eR2x4i", 
        "cmdId": "1", 
        "type": "discoveryInfo", 
        "response": "getInfo"
    }, 
    {
        "playerId": "RINCON_949F3EBA4C1801400", 
        "websocketUrl": "wss://192.168.1.240:1443/websocket/api", 
        "householdId": "Sonos_QtdkCCeSLTp2OLw9n9QvZcJrUk.YFDqOIeCRZ2sE7eR2x4i", 
        "restUrl": "https://192.168.1.240:1443/api", 
        "device": {
            "name": "S15", 
            "color": "White", 
            "serialNumber": "94-9F-3E-BA-4C-18:8", 
            "swGen": 2, 
            "capabilities": [
                "PLAYBACK", 
                "CLOUD", 
                "LINE_IN", 
                "AUDIO_CLIP", 
                "FIXED_VOLUME"
            ], 
            "id": "RINCON_949F3EBA4C1801400", 
            "softwareVersion": "63.0-82280-pint-fusion-integ", 
            "apiVersion": "1.24.0-alpha.1+pint-fusion-integ.alpha.63.0-82280", 
            "modelDisplayName": "Connect", 
            "hwVersion": "1.22.1.5-1.1", 
            "model": "S15", 
            "minApiVersion": "1.1.0"
        }, 
        "groupId": "RINCON_949F3EBA4C1801400:3651079181"
    }
]
```

**Websocket client (muse v2)**
```
In [12]: from sonos_museclient.muse_websocket_client_v2 import MuseWebsocketClient
In [13]: from sonos_museclient.websocket_manager import API_V2
In [14]: ws_client_v2 = MuseWebsocketClient("192.168.1.240", subprotocols=[API_V2])
In [15]: ws_client_v2.info.getInfo()
...
INFO:Muse-Websocket:<Thu Oct 29 14:34:14 2020> Sent to 192.168.1.240: 
[
    {
        "playerId": "RINCON_949F3EBA4C1801400", 
        "command": "getInfo", 
        "cmdId": "1", 
        "namespace": "info", 
        "authorization": "bearer cMG4DiCLMtk5JNOd9ZWhTcW0v3G4"
    }, 
    {}
]

INFO:Muse-Websocket:<Thu Oct 29 14:34:15 2020> Received from 192.168.1.240: 
[
    {
        "success": true, 
        "playerId": "RINCON_949F3EBA4C1801400", 
        "namespace": "info", 
        "householdId": "Sonos_QtdkCCeSLTp2OLw9n9QvZcJrUk.YFDqOIeCRZ2sE7eR2x4i", 
        "cmdId": "1", 
        "type": "discoveryInfo", 
        "response": "getInfo"
    }, 
    {
        "playerId": "RINCON_949F3EBA4C1801400", 
        "websocketUrl": "wss://Sonos-949F3EBA4C18.local:1443/websocket/api", 
        "householdId": "Sonos_QtdkCCeSLTp2OLw9n9QvZcJrUk.YFDqOIeCRZ2sE7eR2x4i", 
        "restUrl": "https://Sonos-949F3EBA4C18.local:1443/api", 
        "device": {
            "name": "S15", 
            "color": "White", 
            "serialNumber": "94-9F-3E-BA-4C-18:8", 
            "swGen": 2, 
            "capabilities": [
                "PLAYBACK", 
                "CLOUD", 
                "LINE_IN", 
                "AUDIO_CLIP", 
                "FIXED_VOLUME"
            ], 
            "id": "RINCON_949F3EBA4C1801400", 
            "softwareVersion": "63.0-82280-pint-fusion-integ", 
            "apiVersion": "1.24.0-alpha.1+pint-fusion-integ.alpha.63.0-82280", 
            "modelDisplayName": "Connect", 
            "hwVersion": "1.22.1.5-1.1", 
            "model": "S15", 
            "minApiVersion": "1.1.0"
        }, 
        "groupId": "RINCON_949F3EBA4C1801400:3651079181"
    }
]
```
