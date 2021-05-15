# muse_release_version: 1.24.0

class ErrorState(object):
    UNSUPPORTED_CMD = 'ERROR_UNSUPPORTED_COMMAND'
    UNSUPPORTED_NAMESPACE = 'ERROR_UNSUPPORTED_NAMESPACE'
    INVALID_OBJECT_ID = 'ERROR_INVALID_OBJECT_ID'
    MISSING_PARAM = "ERROR_MISSING_PARAMETERS"
    INVALID_PARAM = "ERROR_INVALID_PARAMETER"
    INVALID_SYNTAX = "ERROR_INVALID_SYNTAX"
    COMMAND_FAILED = "ERROR_COMMAND_FAILED"
    DISALLOWED_POLICY = "ERROR_DISALLOWED_BY_POLICY"
    SKIP_LIMIT_REACHED = "ERROR_SKIP_LIMIT_REACHED"
    NON_MUSIC_SOURCE = "Received play for non-muse source"
    AVT_URI_CHANGED = "AV Transport URI changed"
    MISSING_BODY = "Missing command body"
    REPLACED = "Replaced"
    NOT_CAPABLE = "ERROR_NOT_CAPABLE"
    AUDIO_CLIP_ID_NOT_FOUND = "ERROR_AUDIO_CLIP_ID_NOT_FOUND"
    PRECONDITON_CHECK_FAILED = "ERROR_PRECONDITION_CHECK_FAILED"
    NO_CONTENT = 'ERROR_PLAYBACK_NO_CONTENT'
    PLAYBACK_FAILED = 'ERROR_PLAYBACK_FAILED'
    CLOUD_QUEUE_SERVER_ERROR = 'ERROR_CLOUD_QUEUE_SERVER'
    CLOUD_QUEUE_SERVICE_ERROR = 'ERROR_CLOUD_QUEUE_SERVICE_ERROR'
    UNSUPPORTED_FORMAT = 'ERROR_UNSUPPORTED_FORMAT'
    UNREACHABLE = 'ERROR_CANT_REACH_SERVER'
    NO_ACCOUNT = 'ERROR_SONOS_NO_ACCOUNT'
    ACCOUNT_INVALID_ID = "ERROR_ACCOUNT_INVALID_ID"
    ACCOUNT_WRONG_SERVICE = "ERROR_ACCOUNT_WRONG_SERVICE"
    ACCOUNT_NO_DEFAULT_FOUND = 'ERROR_ACCOUNT_NO_DEFAULT_FOUND'
    INVALID_API_KEY = "ERROR_API_KEY_VALIDATION_FAILED"
    DEACTIVATION_WRONG_STATE = "ERROR_DEACTIVATION_WRONG_STATE"
    ERROR_AREAS_READ_ONLY = "ERROR_AREAS_READ_ONLY"
    ERROR_NYI = "ERROR_NYI"


class GroupState(object):
    GONE = 'GROUP_STATUS_GONE'
    MOVED = 'GROUP_STATUS_MOVED'
    UPDATED = 'GROUP_STATUS_UPDATED'
    BECAME_COORDINATOR_OF_STANDALONE_GROUP = "Became Coordinator of Standalone Group"


class SessionState(object):
    CONNECTED = "SESSION_STATE_CONNECTED"
    SESSION_JOIN_FAILED = "ERROR_SESSION_JOIN_FAILED"
    SESSION_IN_PROGRESS = "ERROR_SESSION_IN_PROGRESS"
    SESSION_MOVED = 'ERROR_SESSION_MOVED'
    SESSION_EVICTED = "ERROR_SESSION_EVICTED"
    GROUP_CHANGED = "ERROR_GROUP_CHANGED"


class PlaybackState(object):
    IDLE = "PLAYBACK_STATE_IDLE"
    BUFFERING = "PLAYBACK_STATE_BUFFERING"
    PAUSED = "PLAYBACK_STATE_PAUSED"
    PLAYING = "PLAYBACK_STATE_PLAYING"


class PlayModeState(object):
    REPEAT = 'repeat'
    REPEATONE = 'repeatOne'
    CROSSFADE = 'crossfade'
    SHUFFLE = 'shuffle'

    REPEAT_SET = (REPEAT, True)
    REPEAT_UNSET = (REPEAT, False)
    REPEATONE_SET = (REPEATONE, True)
    REPEATONE_UNSET = (REPEATONE, False)
    CROSSFADE_SET = (CROSSFADE, True)
    CROSSFADE_UNSET = (CROSSFADE, False)
    SHUFFLE_SET = (SHUFFLE, True)
    SHUFFLE_UNSET = (SHUFFLE, False)


class Accountstate(object):
    """
    This indicates when an account is active or inactive. This enum does not indicate the current microphone state. An account may be active while the microphone is disabled.
    """
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    INACTIVE = "INACTIVE"

class Alarmtype(object):
    """
    Class description is missing
    """
    LOCAL_ALARM = "LOCAL_ALARM"
    LOCAL_TIMER = "LOCAL_TIMER"
    LOCAL_REMINDER = "LOCAL_REMINDER"

class Ancmode(object):
    """
    Class description is missing
    """
    FULL_NOISE_CANCELLATION = "FULL_NOISE_CANCELLATION"
    HEAR_THROUGH = "HEAR_THROUGH"
    ANC_INACTIVE = "ANC_INACTIVE"

class Audioclipstate(object):
    """
    This enumeration identifies the current status of an audio clip.
    """
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    DISMISSED = "DISMISSED"
    INACTIVE = "INACTIVE"
    INTERRUPTED = "INTERRUPTED"
    ERROR = "ERROR"

class Audiocliptype(object):
    """
    This enumeration identifies the sounds that are built into the Sonos firmware. Partners are free to use these sounds with the loadAudioClip command instead of providing custom files.
    """
    CHIME = "CHIME"
    CUSTOM = "CUSTOM"
    VOICE_ASSISTANT = "VOICE_ASSISTANT"

class Batteryusagepolicy(object):
    """
    Class description is missing
    """
    ALWAYS_READY = "ALWAYS_READY"
    NORMAL = "NORMAL"
    BATTERY_SAVER = "BATTERY_SAVER"

class Cachename(object):
    """
    The cacheName enumeration provides a set of unique identifiers for various caches that exist on the player. These cache identifiers allow a specific cache to be selected upon which an operation (like a clear command) can be performed. For example, the platformInternal namespace's invalidateCache command will expire the contents of a provided cacheName.
    """
    AUTHZTOKENS = "AUTHZTOKENS"
    AUTHZPOLICIES = "AUTHZPOLICIES"
    ENTITLEMENTS = "ENTITLEMENTS"
    SETTINGS = "SETTINGS"
    HISTORY = "HISTORY"

class Capability(object):
    """
    Class description is missing
    """
    PLAYBACK = "PLAYBACK"
    CLOUD = "CLOUD"
    HT_PLAYBACK = "HT_PLAYBACK"
    HT_POWER_STATE = "HT_POWER_STATE"
    AIRPLAY = "AIRPLAY"
    LINE_IN = "LINE_IN"
    AUDIO_CLIP = "AUDIO_CLIP"
    VOICE = "VOICE"
    SPEAKER_DETECTION = "SPEAKER_DETECTION"
    FIXED_VOLUME = "FIXED_VOLUME"
    ROOM_DETECTION = "ROOM_DETECTION"

class Chargingstate(object):
    """
    Class description is missing
    """
    CHARGING = "CHARGING"
    NOT_CHARGING = "NOT_CHARGING"
    CHARGER_NOT_COMPATIBLE = "CHARGER_NOT_COMPATIBLE"

class Clipbehavior(object):
    """
    Class description is missing
    """
    PAUSE_CONTENT = "PAUSE_CONTENT"
    PLAY_TO_BONDED = "PLAY_TO_BONDED"

class Connectionstatus(object):
    """
    Class description is missing
    """
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"

class Contentresourcetype(object):
    """
    Used by the search request command to filter which types of content results are returned.
    """
    ALBUM = "ALBUM"
    ARTIST = "ARTIST"
    AUDIOBOOK = "AUDIOBOOK"
    CHAPTER = "CHAPTER"
    SMAPI_CONTAINER = "SMAPI_CONTAINER"
    EPISODE = "EPISODE"
    PLAYLIST = "PLAYLIST"
    PODCAST = "PODCAST"
    PROGRAM = "PROGRAM"
    STREAM = "STREAM"
    TRACK = "TRACK"

class Diagnosticsubmissionstatus(object):
    """
    Class description is missing
    """
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class Diagnostictype(object):
    """
    Class description is missing
    """
    HEALTHCHECK = "HEALTHCHECK"
    SERVER = "SERVER"
    USER = "USER"
    SNF = "SNF"
    FEEDBACK = "FEEDBACK"

class Disconnectedreason(object):
    """
    Class description is missing
    """
    BLUETOOTH = "BLUETOOTH"
    SLEEPING = "SLEEPING"
    POWERED_OFF = "POWERED_OFF"
    UPGRADE = "UPGRADE"
    NEW_SSID = "NEW_SSID"
    NEW_IP = "NEW_IP"
    UNKNOWN = "UNKNOWN"

class Entitlementcode(object):
    """
    This enumeration represents a group of unique identifiers for the atomic entitlement.
    """
    SRADIO_NO_ADS = "SRADIO_NO_ADS"
    SRADIO_HD_CONTENT = "SRADIO_HD_CONTENT"
    SRADIO_SPECIAL_CONTENT = "SRADIO_SPECIAL_CONTENT"
    SRADIO_ONDEMAND_ARCHIVE = "SRADIO_ONDEMAND_ARCHIVE"
    SRADIO_CAN_SKIP = "SRADIO_CAN_SKIP"
    SFB_BASIC_UI = "SFB_BASIC_UI"
    SFB_COMMERCIAL_MSP = "SFB_COMMERCIAL_MSP"
    SFB_CNTRL_MEDIA_SRCS = "SFB_CNTRL_MEDIA_SRCS"
    SFB_CNTRL_THIRD_PARTY = "SFB_CNTRL_THIRD_PARTY"
    SFB_RSTC_CONTENT_ACS = "SFB_RSTC_CONTENT_ACS"
    SFB_RSTC_SAVE_CONTENT_ACS = "SFB_RSTC_SAVE_CONTENT_ACS"
    SFB_RSTC_SETTINGS_ACS = "SFB_RSTC_SETTINGS_ACS"
    SFB_RSTC_ALARMS_ACS = "SFB_RSTC_ALARMS_ACS"
    SFB_RSTC_MESSAGING_ACS = "SFB_RSTC_MESSAGING_ACS"
    SFB_RSTC_SAVE_GROUPS_ACS = "SFB_RSTC_SAVE_GROUPS_ACS"

class Entitlementtype(object):
    """
    This enumeration represents a grouping classification for an entitlement.
    """
    SONOS_RADIO = "SONOS_RADIO"
    SFB_MVP = "SFB_MVP"

class Ethernetlinkstatus(object):
    """
    Class description is missing
    """
    UP = "UP"
    DOWN = "DOWN"

class Groupstatuscodes(object):
    """
    Class description is missing
    """
    GROUP_STATUS_GONE = "GROUP_STATUS_GONE"
    GROUP_STATUS_MOVED = "GROUP_STATUS_MOVED"
    GROUP_STATUS_UPDATED = "GROUP_STATUS_UPDATED"

class Linktype(object):
    """
    Class description is missing
    """
    UPSELL = "UPSELL"

class Networkingmode(object):
    """
    Class description is missing
    """
    BLUETOOTH = "BLUETOOTH"
    WIFI = "WIFI"

class Personalcatalogsource(object):
    """
    A data source type for personal catalog resources.
    """
    SONOS_FAVORITES = "SONOS_FAVORITES"
    SONOS_PLAYLISTS = "SONOS_PLAYLISTS"
    SONOS_RECENTLY_PLAYED = "SONOS_RECENTLY_PLAYED"
    SERVICE_PERSONALIZATION = "SERVICE_PERSONALIZATION"

class Playbackstate(object):
    """
    Class description is missing
    """
    PLAYBACK_STATE_IDLE = "PLAYBACK_STATE_IDLE"
    PLAYBACK_STATE_BUFFERING = "PLAYBACK_STATE_BUFFERING"
    PLAYBACK_STATE_PAUSED = "PLAYBACK_STATE_PAUSED"
    PLAYBACK_STATE_PLAYING = "PLAYBACK_STATE_PLAYING"

class Powerpolicy(object):
    """
    This enumeration identifies the power policy.
    """
    STAY_AWAKE = "STAY_AWAKE"

class Preferredrecentplay(object):
    """
    This defines the preference of recently played container. When play button is pressed on player while queue is empty, player will send a request to history service to get one container to play, this enum determines whether/which container player will get.
    """
    NONE = "NONE"
    RECENT = "RECENT"
    RANDOM = "RANDOM"

class Priority(object):
    """
    Sonos uses this enumeration to order concurrent clips.
    """
    LOW = "LOW"
    HIGH = "HIGH"

class Queueaction(object):
    """
    Class description is missing
    """
    REPLACE = "REPLACE"
    APPEND = "APPEND"
    INSERT = "INSERT"
    INSERT_NEXT = "INSERT_NEXT"

class Ratingconnotations(object):
    """
    Class description is missing
    """
    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"

class Ratingstates(object):
    """
    Class description is missing
    """
    UNRATED = "UNRATED"
    RATED = "RATED"

class Ratingtypes(object):
    """
    Class description is missing
    """
    STAR = "STAR"
    THUMBSUP = "THUMBSUP"
    THUMBSDOWN = "THUMBSDOWN"
    LOVE = "LOVE"
    HATE = "HATE"
    BAN = "BAN"
    NONE = "NONE"
    SHELVED = "SHELVED"

class Searchcatalogtype(object):
    """
    Describes which type of catalog within which to perform a search request.
    """
    GLOBAL = "GLOBAL"
    PERSONAL = "PERSONAL"

class Searcherrorcode(object):
    """
    Class description is missing
    """
    ERROR_SERVICE_NOT_SEARCHABLE = "ERROR_SERVICE_NOT_SEARCHABLE"
    ERROR_SERVICE_NOT_AVAILABLE = "ERROR_SERVICE_NOT_AVAILABLE"
    ERROR_SERVICE_NOT_CONFIGURED = "ERROR_SERVICE_NOT_CONFIGURED"
    ERROR_ACCOUNT_REAUTH_REQUIRED = "ERROR_ACCOUNT_REAUTH_REQUIRED"
    ERROR_ACCOUNT_UPGRADE_REQUIRED = "ERROR_ACCOUNT_UPGRADE_REQUIRED"
    ERROR_INVALID_SESSION_ID = "ERROR_INVALID_SESSION_ID"

class Searchrank(object):
    """
    Defines the ranking mechanism to be used when returning search results.
    """
    RESOURCE = "RESOURCE"
    TOP = "TOP"
    RELEVANCE = "RELEVANCE"

class Serviceaccounttier(object):
    """
    Defines the tier of a user's music service account.
    """
    NONE = "NONE"
    FREE = "FREE"
    PAIDLIMITED = "PAIDLIMITED"
    PAIDPREMIUM = "PAIDPREMIUM"

class Sessionstateenum(object):
    """
    Class description is missing
    """
    SESSION_STATE_CONNECTED = "SESSION_STATE_CONNECTED"

class Speakerdetectionerror(object):
    """
    Class description is missing
    """
    KNOWN_BUT_MISMATCHED = "KNOWN_BUT_MISMATCHED"
    LEFT_FOUND_RIGHT_UNK = "LEFT_FOUND_RIGHT_UNK"
    RIGHT_FOUND_LEFT_UNK = "RIGHT_FOUND_LEFT_UNK"
    TIMEOUT = "TIMEOUT"
    LR_OPEN_CIRCUIT = "LR_OPEN_CIRCUIT"
    UNK_FOUND = "UNK_FOUND"
    ABORTED = "ABORTED"
    FAIL_CAL = "FAIL_CAL"
    FAIL_MEASURE = "FAIL_MEASURE"
    FAIL_STATUS = "FAIL_STATUS"
    FAIL_UNKNOWN = "FAIL_UNKNOWN"

class Speakerdetectionresult(object):
    """
    Class description is missing
    """
    SUCCESS = "SUCCESS"
    SUCCESS_LEFT_ONLY = "SUCCESS_LEFT_ONLY"
    SUCCESS_RIGHT_ONLY = "SUCCESS_RIGHT_ONLY"
    FAILURE = "FAILURE"

class Syncoperation(object):
    """
    Class description is missing
    """
    PUSH = "PUSH"
    PULL = "PULL"

class Syncsettingtype(object):
    """
    Class description is missing
    """
    MUSIC_ACCOUNTS = "MUSIC_ACCOUNTS"

class Tagsdata(object):
    """
    This generic enum is used to identify information about content. It is too generic, as only one key has been defined in 5 years. Therefore, this enum is deprecated in favor of the `explicit` parameter.
    """
    TAG_EXPLICIT = "TAG_EXPLICIT"

class Transitiontoshipmodeerror(object):
    """
    This type enumerates the various exteneded error details possible from the hardwareStatus.transitionToShipMode command. In many of these cases, the next thing the caller should do is call getBatteryStatus.getBatteryStatus to get more battery information
    """
    INTERNAL_FAILURE = "INTERNAL_FAILURE"
    DEVICE_ACTIVELY_SUSPENDING = "DEVICE_ACTIVELY_SUSPENDING"
    NOT_FACTORY_RESET = "NOT_FACTORY_RESET"
    INADEQUATE_CHARING_POWER_SOURCE = "INADEQUATE_CHARING_POWER_SOURCE"
    NO_FUNCTIONAL_BATTERY_CONNECTION = "NO_FUNCTIONAL_BATTERY_CONNECTION"
    UNACCEPTABLE_BATTERY_PERCENTAGE = "UNACCEPTABLE_BATTERY_PERCENTAGE"
    UNACCEPTABLE_BATTERY_TEMPERATURE = "UNACCEPTABLE_BATTERY_TEMPERATURE"
    TRANSITIONING_TO_SHIPMODE_FAILURE = "TRANSITIONING_TO_SHIPMODE_FAILURE"

class Tvpowerstate(object):
    """
    This enum represents the options to control the TV power state. More states could be added in the future.
    """
    ON = "ON"
    STANDBY = "STANDBY"

class Usagecontext(object):
    """
    Class description is missing
    """
    BUSINESS = "BUSINESS"
    EXTERNAL_PARTNER = "EXTERNAL_PARTNER"

class Virtuallineintype(object):
    """
    Class description is missing
    """
    AIRPLAY = "AIRPLAY"

class Voiceservice(object):
    """
    This enumeration identifies the integrated voice services.
    """
    AMAZON = "AMAZON"
    GOOGLE = "GOOGLE"
    SVE = "SVE"

class Voicevariant(object):
    """
    This enumeration identifies the active wakeword.
    """
    ALEXA = "ALEXA"
    HEY_SONOS = "HEY_SONOS"

class Volumemode(object):
    """
    Class description is missing
    """
    VARIABLE = "VARIABLE"
    FIXED = "FIXED"
    PASS_THROUGH = "PASS_THROUGH"

class Wirelessnetworktype(object):
    """
    Describes the type of wireless network the device is currently using to communicate with other Sonos devices in the household.
    """
    SONOSNET = "SONOSNET"
    STATION = "STATION"
    DISCONNECTED = "DISCONNECTED"

