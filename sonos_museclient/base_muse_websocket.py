import websocket
import logging
from muse_rest_client import BaseRestClient
from muse_events import MuseEvent
import json
import time
import inspect
import ssl
import copy
import re
try:
    import thread
except ImportError:
    import _thread as thread
import datetime

API_V0 = "v0.api.smartspeaker.audio"
API_V1 = "v1.api.smartspeaker.audio"
API_V2 = "v2.api.smartspeaker.audio"
API_BASE = "/websocket/api"
logging.basicConfig(level=logging.INFO)
wsLogger = logging.getLogger("Muse-Websocket")
wsLogger.setLevel(logging.INFO)


class ConnectionError(Exception):
    """
    Custom exception for websocket connection failure
    """
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

    def __str__(self):
        return "Couldn't establish websocket connection to {} within {}s".format(self.url, self.timeout)


class BaseMuseWebsocket(BaseRestClient):
    @property
    def connected(self):
        if self._ws and self._ws.sock:
            return self._ws.sock.connected
        else:
            return False

    @property
    def sessionId(self):
        return self._sessionId

    @sessionId.setter
    def sessionId(self, sid):
        self._sessionId = sid

    @property
    def cmdId(self):
        return self._cmdId

    @cmdId.setter
    def cmdId(self, id):
        self._cmdId = id

    @property
    def subprotocols(self):
        return self._subprotocols

    def __init__(self, ip, secure=True, hhid=None, uuid=None, apiKey=None,
                 subprotocols=None, port=None, secureOverride=None):
        """
        Opens a websocket connection to the ZP
        :param ip: IP address for ws connection
        :param (optional) secure: ws port, 1400 if not secure, 1443 if it is
        :param (optional) hhid: household ID, if not set it is retrieved automatically from the player
        :param (optional) uuid: Player unique ID, if not set it is retrieved automatically from the player
        :param (optional) api_key: Api key for ws connection
        :param (optional) subprotocols: subprotocols list, used to specify api version
        :param (optional) port: custom port to connect to on the dut
        :param (optional) secureOverride: protocol string override "ws"/"wss"
        """
        super(BaseMuseWebsocket, self).__init__(ip=ip, hhid=hhid, uuid=uuid, apiKey=apiKey,
                                                apiVersion="1", port=port, secureOverride=secureOverride)
        # Private
        self._apiPath = API_BASE
        self._ws = None
        self._port = self.getPort(secure)

        if secureOverride is not None:
            self._protocol = secureOverride
        else:
            self._protocol = "wss" if secure else "ws"

        self._cmdId = 1
        self._subprotocols = [API_V1] if subprotocols is None else subprotocols
        self._sessionId = None

        self.logger = wsLogger

        # Event storage
        self.allEvents = []  # All received events
        self.checkedEvents = []  # All received events that have been processed

        # Make the websocket connection
        self.connect()

    def connect(self, timeout=10):
        """
        Establish websocket connection to given ip
        :param timeout: Timeout in second to wait for the ws connection to establish
        :return:
        """
        url = "{}://{}:{}{}".format(self._protocol, self._ip, self._port, self._apiPath)

        header = None
        if self._apiKey is not None:
            if API_V1 in self._subprotocols or API_V0 in self._subprotocols:
                url += "?key={}".format(self._apiKey)

        self._ws = websocket.WebSocketApp(url, subprotocols=self._subprotocols,
                                          on_open=lambda ws: self._onOpen(ws),
                                          on_message=lambda ws, msg: self._onMessage(ws, msg),
                                          on_error=lambda ws, err: self._onError(ws, err),
                                          on_close=lambda ws: self._onClose(ws),
                                          header=header)
        thread.start_new_thread(self._ws.run_forever, (None,), {"sslopt": {"cert_reqs": ssl.CERT_NONE},
                                                                "ping_interval": 120,
                                                                "ping_timeout": 10})

        end = time.time() + timeout
        while not self.connected and time.time() < end:
            time.sleep(0.2)
        if not self.connected:
            raise ConnectionError(url, timeout)

    def disconnect(self):
        """
        Close the websocket connection
        :return:
        """
        if self.connected:
            self._ws.close()

    def send(self, cmdHeaderBody, raw=False):
        """
        Send a raw ws message to the connected ZP
        :param cmdHeaderBody:
        :param raw:
        :return:
        """
        if raw:
            command = cmdHeaderBody
        else:
            command = json.dumps(cmdHeaderBody, encoding='utf-8', ensure_ascii=False,
                                 allow_nan=False, indent=4).encode('utf-8')
        self.logger.info("<{}> Sent to {}: \n{}".format(datetime.datetime.now().ctime(), self._ip, command))
        self._ws.send(command)
        self._cmdId += 1

    def send_raw(self, cmdHeaderBody):
        """
        Send a raw NON encoded ws message to the connected ZP
        :param cmdHeaderBody:
        :return:
        """
        self.logger.info("<{}> Sent to {}: \n{}".format(datetime.datetime.now().ctime(), self._ip, cmdHeaderBody))
        self._ws.send(cmdHeaderBody)
        self._cmdId += 1

    def _eventTypeMatch(self, classifiedEventList, expectedEventType):
        """
        Filter a list of museEvent types finding only events of type expectedEventType
        :param classifiedEventList:
        :param expectedEventType:
        :return:
        """
        return list(filter(lambda ev: isinstance(ev, expectedEventType), classifiedEventList))

    def _eventFilterMatch(self, eventList, expectedEventFilter):
        """
        Filter a list of museEvent types further by applying a lambda function to each
        :param eventList:
        :param expectedEventFilter:
        :return:
        """
        matched_events = []
        for event in eventList:
            try:
                if expectedEventFilter(event):
                    matched_events.append(event)
            except KeyError:
                # Ignore the event if the expectedEventFilter field returns KeyError (param is not found in the event)
                pass

        return matched_events

    def _classifyEventList(self, eventList):
        """
        Classify a list of base museEvent types into more specific museEvent types
        :param eventList:
        :return:
        """
        return list(map(lambda ev: MuseEvent.classifyEvent(ev), eventList))

    def waitForEvent(self, eventFilter=lambda ev: True, eventType=None, timeout=15, interval=1,
                     assertOnFail=True, expected=True, usePastEvents=False, returnAllMatched=False):
        """
        Polls for given time until a matching event is found.
        :param eventType: event type to check for, a child class of MuseEvent. See muse_events.py
        :param eventFilter: lambda function
        :param timeout: Time (in s) to poll for matching event
        :param interval: Time (in s) to pause during check iterations
        :param assertOnFail: bool, should this function assert in failure cases?
        :param expected: bool, should the caller expect a matched event to return?
        :param usePastEvents: should the unprocessed_event list be all events received in a test case on the first loop?
        :param returnAllMatched: bool, return all matched events or just the first one?
        :return: None if no event found, else the parsed MuseEvent subclass
        """
        # Save the eventFilter lambda as a string
        try:
            rawEventFilterString = ' '.join([l.strip() for l in inspect.getsource(eventFilter).splitlines()])
            filterStr = "lambda{}".format(re.search('lambda(.+?),', rawEventFilterString).group(1))
        except Exception:
            filterStr = None
        # Save the eventType class name as a string
        try:
            eventClassName = eventType.__name__
        except Exception:
            eventClassName = None

        discardedEvents = []

        end = time.time() + timeout
        while time.time() < end:
            # Determine if we want to look at all past events on the first loop through
            if usePastEvents:
                # Set unprocessed_event list to allEvents if we want to re-process all events received
                # this will include any new events that have not been previously processed
                unprocessedEvents = copy.deepcopy(self.allEvents)
            else:
                # Get the difference between already processed events and the all events list
                # The resulting list should be all unprocessed events
                unprocessedEvents = [x for x in self.allEvents if x not in self.checkedEvents]

            if len(unprocessedEvents) > 0:
                if usePastEvents:
                    # just make a copy of allEvents to checkedEvents if we're re-processing all previous events
                    # this will include any new events that have not been previously processed
                    self.checkedEvents = copy.deepcopy(self.allEvents)
                else:
                    # append just the previously unprocessed events to the processed events list
                    self.checkedEvents.extend(unprocessedEvents)

                # Use the eventType param to determine if we want to do type matching here
                if eventType is not None:
                    # Do event type matching if a type is specified
                    unprocessedEvents = self._classifyEventList(unprocessedEvents)
                    matchedTypeEvents = self._eventTypeMatch(unprocessedEvents, eventType)
                    # apply event filter to matched type event list
                    matchedEvents = self._eventFilterMatch(matchedTypeEvents, eventFilter)
                else:
                    # apply event filter to just the new events list
                    matchedEvents = self._eventFilterMatch(unprocessedEvents, eventFilter)

                try:
                    matchedEvent = matchedEvents[0]
                except IndexError:
                    # IndexError means we failed to find any event that matched the supplied type/filter
                    if expected:
                        # If we're expecting an event to be found, keep looping
                        self.logger.warning(
                            "Discarded events for eventType: <{}>, eventFilter: <{}>".format(eventClassName,
                                                                                             filterStr))
                        # Log out all the events processed during this loop cycle
                        for evt in unprocessedEvents:
                            self.logger.warning("DISCARDED EVENT: \n<{}>\n<{}>".format(evt.__class__.__name__,
                                                                                       evt))
                            discardedEvents.append(evt)
                else:
                    # We've found a matching event, process according to whether its expected or not
                    if not expected and assertOnFail:
                        # Only assert on unexpected found event if assertOnFail is True
                        assert False, \
                            "Found unexpected event(s) for eventType: <{}>, eventFilter: <{}>".format(
                                eventClassName, filterStr)
                    # Return the matched event(s) regardless whether we expected it or not if assertOnFail is False
                    # Its up the test case writer to handle the returned event(s)
                    if returnAllMatched:
                        return matchedEvents
                    else:
                        return matchedEvent
            # We've processed all past events on the first loop so set usePastEvents to False
            usePastEvents = False
            self.logger.warning("No matched event found, waiting <{}> seconds for more events".format(interval))
            time.sleep(interval)

        # At this point, we've failed to find a matching event
        if assertOnFail and expected:
            # If we expected to find something, this is a failure state. Assert here if desired
            discarded = [str(d) for d in discardedEvents]
            message = "Discarded events"

            # Cap last 5 events to prevent log spam
            if len(discarded) > 5:
                message = "\nLast 5 discarded events"
                discarded = discarded[-5:]

            discarded = ",\n\n".join(discarded)
            assert False,\
                "No matched events after <{}> secs for eventType: <{}>, eventFilter: <{}>\n{}:\n\n{}".format(
                    timeout, eventClassName, filterStr, message, discarded)
        else:
            # If no assert is desired here, just return None for the test writer to handle
            return None
# endregion

# region WS Handling
    def _onMessage(self, ws, message):
        """
        Called when a message is received on the ws connection
        :param ws:
        :param message:
        :return:
        """
        self.logger.info("<{}> Received from {}: \n{}".format(datetime.datetime.now().ctime(), self._ip,
                                                              json.dumps(json.loads(message), indent=4)))
        # Do some basic parsing to break up the message into header/body objects
        museEvent = MuseEvent.parseRaw(message)
        # Add events to allEvents list
        self.allEvents.append(museEvent)
        # Set sessionId if the message has a sessionId param in the body
        if "sessionId" in museEvent.body:
            sessionId = museEvent.body["sessionId"].encode('ascii')
            self.logger.info("New sessionId: {}".format(sessionId))
            self.sessionId = sessionId

    def _onError(self, ws, error):
        """
        Called when an error is thrown on the ws connection
        :param ws:
        :param error:
        :return:
        """
        self.logger.error(str(error))

    def _onClose(self, ws):
        """
        Called when the ws connection closes
        :param ws:
        :return:
        """
        self.logger.info("<{}> Closed ws connection to: {}\n".format(datetime.datetime.now().ctime(), ws.url))

    def _onOpen(self, ws):
        """
        Called when the ws connection opens
        :param ws:
        :return:
        """
        self.logger.info("<{}> Opened ws connection to: {}\n".format(datetime.datetime.now().ctime(), ws.url))
# endregion
