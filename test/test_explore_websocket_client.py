import pytest
from sonos_museclient.muse_websocket_client import MuseWebsocketClient
from sonos_museclient.muse_events import MuseSuccessEvent, PlaybackStatusEvent, PlayerVolumeEvent, MetadataStatusEvent, SessionStatusEvent

@pytest.fixture(scope="function")
def muse():
    muse = MuseWebsocketClient(ip="10.25.92.209")
    yield muse
    muse.disconnect()


def test_muse_successful_event_match(muse):
    """
    Demo various successful uses of the the waitForEvent function
    :param muse:
    :return:
    """
    muse.playback.getPlaybackStatus()
    # Wait for specific event type, no event filter
    ev = muse.waitForEvent(eventType=PlaybackStatusEvent)
    # Verify waitForEvent returns the specific event
    assert ev is not None, "waitForEvent should not return None"

    muse.playback.getPlaybackStatus()
    # Wait for specific event with event filter
    muse.waitForEvent(lambda e: "IDLE" in e.playbackState, eventType=PlaybackStatusEvent)

    muse.playback.getPlaybackStatus()
    # Wait for specific event with filter only, disable the event internal event classification
    # In this case, waitForEvent returns a generic event with header/body attributes
    muse.waitForEvent(lambda e: "IDLE" in e.body["playbackState"], eventType=None)

    muse.playbackMetadata.getMetadataStatus()
    muse.playback.getPlaybackStatus()
    # If not using event classification, use a more detailed filter
    # If just using the "IDLE" check, this will cause an attribute error since "playbackState" does not
    # exist in the metadataStatus event body
    muse.waitForEvent(lambda e: ("playbackState" in e.body and
                                 "IDLE" in e.body["playbackState"]), eventType=None)

    muse.playback.getPlaybackStatus()
    # Wait for unexpected event type, no filter
    ev = muse.waitForEvent(eventType=SessionStatusEvent, expected=False, timeout=2)
    assert ev is None, "waitForEvent should return None"

    muse.playback.getPlaybackStatus()
    # Wait for unexpected event type that passes event filter
    muse.waitForEvent(lambda e: "PLAYING" in e.playbackState, eventType=PlaybackStatusEvent,
                        expected=False, timeout=2)

    muse.playback.getPlaybackStatus()
    # Wait for unexpected event that passes filter, no event classification
    muse.waitForEvent(lambda e: "PLAYING" in e.body["playbackState"], eventType=None,
                      expected=False, timeout=2)

    muse.waitForEvent(eventType=MetadataStatusEvent, usePastEvents=True)


def test_muse_unsuccessful_event_matching(muse):
    """
    Demo various error states of the the waitForEvent function
    Mostly disabling assertOnFail so that the test case will pass
    :param muse:
    :return:
    """
    muse.playback.getPlaybackStatus()
    # Failure due to not finding event type
    ev = muse.waitForEvent(eventType=SessionStatusEvent, assertOnFail=False)
    assert ev is None, "waitForEvent should return None"

    muse.playback.getPlaybackStatus()
    # Failure due to correct event type not passing event filter
    ev = muse.waitForEvent(lambda e: "PLAYING" in e.playbackState, eventType=PlaybackStatusEvent,
                           assertOnFail=False)
    assert ev is None, "waitForEvent should return None"

    muse.playback.getPlaybackStatus()
    # Failure due to not passing event filter, no event classification
    ev = muse.waitForEvent(lambda e: "PLAYING" in e.body["playbackState"], eventType=None,
                           assertOnFail=False)
    assert ev is None, "waitForEvent should return None"

    muse.playback.getPlaybackStatus()
    # Failure due to finding unexpected event type
    ev = muse.waitForEvent(eventType=PlaybackStatusEvent, expected=False, assertOnFail=False, timeout=2)
    # should return the unexpected event
    assert ev is not None, "waitForEvent should not return None"

    muse.playback.getPlaybackStatus()
    # Failure due to unexpected event type and passing event filter
    ev = muse.waitForEvent(lambda e: "IDLE" in e.playbackState, eventType=PlaybackStatusEvent,
                           expected=False, assertOnFail=False, timeout=2)
    assert ev is not None, "waitForEvent should not return None"

    muse.playback.getPlaybackStatus()
    # Failure due to unexpected event passing only a filter, no event classification
    ev = muse.waitForEvent(lambda e: "IDLE" in e.body["playbackState"], eventType=None,
                           expected=False, assertOnFail=False, timeout=2)
    assert ev is not None, "waitForEvent should not return None"

    try:
        muse.playback.getPlaybackStatus()
        # This should assert since assertOnFail defaults to True
        muse.waitForEvent(eventType=SessionStatusEvent)
    except:
        muse.logger.info("Should have asserted here")
    else:
        assert False, "No assertion found!"
