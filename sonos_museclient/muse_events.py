# muse_release_version: 1.24.0
import inspect
import json
import pprint
import sys


class MuseParsingError(Exception):
    pass


class MuseEvent(object):
    def __init__(self, header, body):
        """
        Generic muse-style event
        :param header: Json dictionary of a valid muse header
        :param body: Json dictionary of a valid muse header
        """
        self.header = header
        self.body = body

        # All muse commands should have type and namespace elements
        self.type = self.header["type"]
        self.namespace = self.header["namespace"]

    def __str__(self):
        return pprint.pformat([self.header, self.body])

    @staticmethod
    def parseRaw(wsMessage):
        """
        Parse raw incoming websocket messages
        :param wsMessage:
        :return:
        """
        messageJson = json.loads(wsMessage)
        if len(messageJson) != 2:
            raise MuseParsingError("Malformed websocket message, expected header-body format, got <{}>"
                                   .format(wsMessage))

        return MuseEvent(messageJson[0], messageJson[1])

    @staticmethod
    def classifyEvent(genericMuseEvent):
        """
        Factory method that parses the given muse-style message into a known event type, if possible
        :param genericMuseEvent: classified generic muse event
        :return: Classified muse event object, deriving from MuseEvent
        """
        # set the classified event to the generic type to begin with
        museEvent = MuseEvent(genericMuseEvent.header,
                              genericMuseEvent.body)
        try:
            if "success" in genericMuseEvent.header:
                if genericMuseEvent.header["success"] and len(genericMuseEvent.body) == 0:
                    # Do a generic success match if the event is a success and it has no body stuff
                    # probably a response to a sub/unsub command
                    museEvent = MuseSuccessEvent(genericMuseEvent.header,
                                                 genericMuseEvent.body)
                elif not genericMuseEvent.header["success"]:
                    # If its not successful, its probably an error event
                    museEvent = MuseErrorEvent(genericMuseEvent.header,
                                               genericMuseEvent.body)
            if "success" not in genericMuseEvent.header or len(genericMuseEvent.body) > 0:
                # If the event doesn't have "success" param or if it has body stuff, try to do event type matching
                # Look through all of the defined event types and try to find a match
                event_class = genericMuseEvent.header["type"] + "Event"
                # Capitalize the event_class
                event_class = event_class[:1].upper() + event_class[1:]
                if event_class in ALL_MUSE_EVENTS:
                    # If match is found, create an instance of that class
                    matched_class = getattr(sys.modules[__name__], event_class)
                    museEvent = matched_class(genericMuseEvent.header,
                                              genericMuseEvent.body)
            return museEvent
        except Exception as ex:
            raise MuseParsingError("Error parsing muse event: {}\n\t{}".format(str(ex), genericMuseEvent))


class MuseErrorEvent(MuseEvent):
    def __init__(self, header, body):
        super(MuseErrorEvent, self).__init__(header, body)


class MuseSuccessEvent(MuseEvent):
    def __init__(self, header, body):
        super(MuseSuccessEvent, self).__init__(header, body)


class AlarmEvent(MuseEvent):
    def __init__(self, header, body):
        super(AlarmEvent, self).__init__(header, body)

        self.token = self.body.get("token")
        self.payload = self.body.get("payload")
        self.started = self.body.get("started")
        self.scheduledTime = self.body.get("scheduledTime")
        self.type = self.body.get("type")
        self.howLateInSeconds = self.body.get("howLateInSeconds")


class AudioClipStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(AudioClipStatusEvent, self).__init__(header, body)

        self.audioClips = self.body.get("audioClips")


class ClientStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(ClientStatusEvent, self).__init__(header, body)

        self.cloudSubscriptions = self.body.get("cloudSubscriptions")


class CloudRegistrationStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(CloudRegistrationStatusEvent, self).__init__(header, body)


class DevicesEvent(MuseEvent):
    def __init__(self, header, body):
        super(DevicesEvent, self).__init__(header, body)

        self.devices = self.body.get("devices")


class DiagnosticMetadataEvent(MuseEvent):
    def __init__(self, header, body):
        super(DiagnosticMetadataEvent, self).__init__(header, body)

        self.metadata = self.body.get("metadata")


class DiagnosticSubmissionResultsEvent(MuseEvent):
    def __init__(self, header, body):
        super(DiagnosticSubmissionResultsEvent, self).__init__(header, body)

        self.results = self.body.get("results")


class ExtendedPlaybackStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(ExtendedPlaybackStatusEvent, self).__init__(header, body)

        self.playback = self.body.get("playback")
        self.playbackError = self.body.get("playbackError")
        self.metadata = self.body.get("metadata")


class GroupCoordinatorChangedEvent(MuseEvent):
    def __init__(self, header, body):
        super(GroupCoordinatorChangedEvent, self).__init__(header, body)

        self.groupStatus = self.body.get("groupStatus")
        self.groupName = self.body.get("groupName")
        self.websocketUrl = self.body.get("websocketUrl")
        self.playerId = self.body.get("playerId")


class GroupVolumeEvent(MuseEvent):
    def __init__(self, header, body):
        super(GroupVolumeEvent, self).__init__(header, body)

        self.volume = self.body.get("volume")
        self.muted = self.body.get("muted")
        self.fixed = self.body.get("fixed")


class GroupsEvent(MuseEvent):
    def __init__(self, header, body):
        super(GroupsEvent, self).__init__(header, body)

        self.groups = self.body.get("groups")
        self.players = self.body.get("players")
        self.partial = self.body.get("partial")


class MetadataStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(MetadataStatusEvent, self).__init__(header, body)


class PlaybackErrorEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlaybackErrorEvent, self).__init__(header, body)

        self.errorCode = self.body.get("errorCode")
        self.reason = self.body.get("reason")
        self.itemId = self.body.get("itemId")
        self.host = self.body.get("host")
        self.hostIp = self.body.get("hostIp")
        self.httpStatus = self.body.get("httpStatus")
        self.queueVersion = self.body.get("queueVersion")


class PlaybackStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlaybackStatusEvent, self).__init__(header, body)

        self.playbackState = self.body.get("playbackState")
        self.isDucking = self.body.get("isDucking")
        self.queueVersion = self.body.get("queueVersion")
        self.itemId = self.body.get("itemId")
        self.positionMillis = self.body.get("positionMillis")
        self.previousItemId = self.body.get("previousItemId")
        self.previousPositionMillis = self.body.get("previousPositionMillis")
        self.playModes = self.body.get("playModes")
        self.availablePlaybackActions = self.body.get("availablePlaybackActions")


class PlayerVolumeEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlayerVolumeEvent, self).__init__(header, body)

        self.volume = self.body.get("volume")
        self.muted = self.body.get("muted")
        self.fixed = self.body.get("fixed")


class SessionErrorEvent(MuseEvent):
    def __init__(self, header, body):
        super(SessionErrorEvent, self).__init__(header, body)

        self.errorCode = self.body.get("errorCode")
        self.reason = self.body.get("reason")


class SessionInfoEvent(MuseEvent):
    def __init__(self, header, body):
        super(SessionInfoEvent, self).__init__(header, body)

        self.suspended = self.body.get("suspended")


class UpnpEventEvent(MuseEvent):
    def __init__(self, header, body):
        super(UpnpEventEvent, self).__init__(header, body)


class VersionChangedEvent(MuseEvent):
    def __init__(self, header, body):
        super(VersionChangedEvent, self).__init__(header, body)


class TransitionToShipModeStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(TransitionToShipModeStatusEvent, self).__init__(header, body)


class UpnpResponseEvent(MuseEvent):
    def __init__(self, header, body):
        super(UpnpResponseEvent, self).__init__(header, body)


class RecommendationResultsEvent(MuseEvent):
    def __init__(self, header, body):
        super(RecommendationResultsEvent, self).__init__(header, body)


class NetworkTestResultEvent(MuseEvent):
    def __init__(self, header, body):
        super(NetworkTestResultEvent, self).__init__(header, body)


class EntitlementsListEvent(MuseEvent):
    def __init__(self, header, body):
        super(EntitlementsListEvent, self).__init__(header, body)


class ChirpRequestEvent(MuseEvent):
    def __init__(self, header, body):
        super(ChirpRequestEvent, self).__init__(header, body)


class FavoritesListEvent(MuseEvent):
    def __init__(self, header, body):
        super(FavoritesListEvent, self).__init__(header, body)


class BluetoothEvent(MuseEvent):
    def __init__(self, header, body):
        super(BluetoothEvent, self).__init__(header, body)


class NetworksListEvent(MuseEvent):
    def __init__(self, header, body):
        super(NetworksListEvent, self).__init__(header, body)


class BatteryCellsEvent(MuseEvent):
    def __init__(self, header, body):
        super(BatteryCellsEvent, self).__init__(header, body)


class PlayerSettingsEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlayerSettingsEvent, self).__init__(header, body)


class DiagnosticInfoEvent(MuseEvent):
    def __init__(self, header, body):
        super(DiagnosticInfoEvent, self).__init__(header, body)


class PlaylistsListEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlaylistsListEvent, self).__init__(header, body)


class TrueplayConfigurationEvent(MuseEvent):
    def __init__(self, header, body):
        super(TrueplayConfigurationEvent, self).__init__(header, body)


class SoundSwapRequestResponseEvent(MuseEvent):
    def __init__(self, header, body):
        super(SoundSwapRequestResponseEvent, self).__init__(header, body)


class SessionStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(SessionStatusEvent, self).__init__(header, body)


class MusicServiceAccountEvent(MuseEvent):
    def __init__(self, header, body):
        super(MusicServiceAccountEvent, self).__init__(header, body)


class DiagnosticSubmissionMetadataEvent(MuseEvent):
    def __init__(self, header, body):
        super(DiagnosticSubmissionMetadataEvent, self).__init__(header, body)


class AreaEvent(MuseEvent):
    def __init__(self, header, body):
        super(AreaEvent, self).__init__(header, body)


class HouseholdsEvent(MuseEvent):
    def __init__(self, header, body):
        super(HouseholdsEvent, self).__init__(header, body)


class BatteryEvent(MuseEvent):
    def __init__(self, header, body):
        super(BatteryEvent, self).__init__(header, body)


class OfflinePskEvent(MuseEvent):
    def __init__(self, header, body):
        super(OfflinePskEvent, self).__init__(header, body)


class GlobalErrorEvent(MuseEvent):
    def __init__(self, header, body):
        super(GlobalErrorEvent, self).__init__(header, body)


class SonosnetEvent(MuseEvent):
    def __init__(self, header, body):
        super(SonosnetEvent, self).__init__(header, body)


class RestrictedAdminSettingsEvent(MuseEvent):
    def __init__(self, header, body):
        super(RestrictedAdminSettingsEvent, self).__init__(header, body)


class ProtectedAdminSettingsEvent(MuseEvent):
    def __init__(self, header, body):
        super(ProtectedAdminSettingsEvent, self).__init__(header, body)


class VoiceAccountEvent(MuseEvent):
    def __init__(self, header, body):
        super(VoiceAccountEvent, self).__init__(header, body)


class AudioClipEvent(MuseEvent):
    def __init__(self, header, body):
        super(AudioClipEvent, self).__init__(header, body)


class WiredSubStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(WiredSubStatusEvent, self).__init__(header, body)


class GroupInfoEvent(MuseEvent):
    def __init__(self, header, body):
        super(GroupInfoEvent, self).__init__(header, body)


class PublicSettingsEvent(MuseEvent):
    def __init__(self, header, body):
        super(PublicSettingsEvent, self).__init__(header, body)


class RateStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(RateStatusEvent, self).__init__(header, body)


class AreasEvent(MuseEvent):
    def __init__(self, header, body):
        super(AreasEvent, self).__init__(header, body)


class SpeakerDetectionStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(SpeakerDetectionStatusEvent, self).__init__(header, body)


class EthernetPortsEvent(MuseEvent):
    def __init__(self, header, body):
        super(EthernetPortsEvent, self).__init__(header, body)


class DiscoveryInfoEvent(MuseEvent):
    def __init__(self, header, body):
        super(DiscoveryInfoEvent, self).__init__(header, body)


class SettingsEvent(MuseEvent):
    def __init__(self, header, body):
        super(SettingsEvent, self).__init__(header, body)


class VoiceAccountsListEvent(MuseEvent):
    def __init__(self, header, body):
        super(VoiceAccountsListEvent, self).__init__(header, body)


class NetworkTestIdEvent(MuseEvent):
    def __init__(self, header, body):
        super(NetworkTestIdEvent, self).__init__(header, body)


class PlaylistSummaryEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlaylistSummaryEvent, self).__init__(header, body)


class HomeTheaterOptionsEvent(MuseEvent):
    def __init__(self, header, body):
        super(HomeTheaterOptionsEvent, self).__init__(header, body)


class WirelessNetworkEvent(MuseEvent):
    def __init__(self, header, body):
        super(WirelessNetworkEvent, self).__init__(header, body)


class PlayerSetErrorEvent(MuseEvent):
    def __init__(self, header, body):
        super(PlayerSetErrorEvent, self).__init__(header, body)


class ContentPagedResourcesEvent(MuseEvent):
    def __init__(self, header, body):
        super(ContentPagedResourcesEvent, self).__init__(header, body)


class AccountErrorEvent(MuseEvent):
    def __init__(self, header, body):
        super(AccountErrorEvent, self).__init__(header, body)


class WirelessNetworkStatusEvent(MuseEvent):
    def __init__(self, header, body):
        super(WirelessNetworkStatusEvent, self).__init__(header, body)


ALL_MUSE_EVENTS = [name for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)]
