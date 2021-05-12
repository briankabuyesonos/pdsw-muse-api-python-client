from muse_websocket_client import MuseWebsocketClient
from muse_websocket_client_v2 import MuseWebsocketClient as MuseWebsocketClientV2
from base_muse_websocket import API_V0, API_V1, API_V2


class ws_manager(object):
    """
    Manage all the websocket connections a test case will use
    """
    def __init__(self):
        """
        Init default values
        """
        # Dict to keep track of all websocket connections to each player a test case uses
        self._ws_connections = {}

    @property
    def ws_connections(self):
        return self._ws_connections

    @ws_connections.setter
    def ws_connections(self, ws_connections):
        self._ws_connections = ws_connections

    def make_connection(self, zp, secure=True, hhid=None, uuid=None, apiKey=None, subprotocols=None):
        """
        Make a websocket connection to a zp.
        :param zp:
        :param secure:
        :param hhid:
        :param uuid:
        :param apiKey:
        :param subprotocols:
        :return:
        """
        # Make the connection
        if subprotocols is None or API_V0 in subprotocols or API_V1 in subprotocols:
            ws_conn = MuseWebsocketClient(ip=zp.ip, secure=secure, hhid=hhid,
                                          uuid=uuid, apiKey=apiKey, subprotocols=subprotocols)
        else:
            ws_conn = MuseWebsocketClientV2(ip=zp.ip, secure=secure, hhid=hhid,
                                            uuid=uuid, subprotocols=subprotocols)

        # Update the ws_connections dict
        if zp not in self.ws_connections or self.ws_connections[zp] is None:
            # Make a new dict entry if the zp doesn't have any previous ws connections
            self.ws_connections[zp] = [ws_conn]
        else:
            # If the zp is already in the dict, just append the new connection to the list associated with it
            self.ws_connections[zp].append(ws_conn)
        return ws_conn

    def disconnect_all(self, zp):
        """
        Disconnect all websocket connections for a given zp
        :param zp:
        :return:
        """
        # Disconnect all websocket connections
        if zp in self.ws_connections and self.ws_connections[zp] is not None:
            for ws in self.ws_connections[zp]:
                ws.disconnect()

            # Clean the connections list associated with the zp
            self.ws_connections[zp] = None

    def disconnect_all_for_all_zps(self):
        """
        Disconnect all websocket connections for all zps
        :return:
        """
        for zp in self.ws_connections:
            if zp is not None:
                self.disconnect_all(zp)

    def reset_manager(self):
        """
        Disconnect all ws connections for all zps in the dict and reset the dictionary
        :return:
        """
        self.disconnect_all_for_all_zps()
        self.ws_connections = {}
