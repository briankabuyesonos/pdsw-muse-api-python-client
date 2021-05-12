from sonos.services.common import wait_until_equal
from base_helper import baseNamespaceHelper
from sonos_museclient.muse_event_enums import PlaybackState


class playbackNamespaceHelpers(baseNamespaceHelper):
    """
    Helper functions that are mainly orientated towards the playback namespace commands
    """
    def __init__(self, restClient):
        super(playbackNamespaceHelpers, self).__init__(restClient=restClient)

    def is_playing(self):
        """
        Is the zp playing?
        :return:
        """
        return self.get_current_playback_state() == PlaybackState.PLAYING

    def is_paused(self):
        """
        Is the zp paused?
        :return:
        """
        return self.get_current_playback_state() == PlaybackState.PAUSED

    def is_idle(self):
        """
        Is the zp idle?
        :return:
        """
        return self.get_current_playback_state() == PlaybackState.IDLE

    def get_current_playback_state(self):
        """
        Get the current playback state
        :return:
        """
        return self._baseMuseClient.playback.getPlaybackStatus()["playbackState"]

    def get_current_play_modes(self):
        """
        Get the current playback mode
        :return:
        """
        return self._baseMuseClient.playback.getPlaybackStatus()["playModes"]

    def wait_for_playback_state(self, playbackState, timeout=10):
        """
        Wait for the zp to be in the expected playback state
        :param playbackState:
        :param timeout:
        :return:
        """
        wait_until_equal(playbackState, lambda: self.get_current_playback_state(),
                         timeout_seconds=timeout, iteration_delay=1,
                         reason="Timed out waiting for {} playback state".format(self._baseMuseClient.ip))

    def wait_for_play_mode_set(self, playModeState, timeout=20):
        """
        Wait for the zp to have the expected play mode set
        :param playModeState:
        :param timeout:
        :return:
        """
        mode = playModeState[0]
        state = playModeState[1]
        wait_until_equal(state, lambda: self.get_current_play_modes()[mode],
                         timeout_seconds=timeout, iteration_delay=1,
                         reason="Timed out waiting for {} to be {}".format(self._baseMuseClient.ip,
                                                                           playModeState))

    def set_play_mode_and_wait(self, playModeState, timeout=10):
        """
        Set the specified play mode
        :param playModeState:
        :return:
        """
        self._baseMuseClient.playback.setPlayModes(playModes=dict([playModeState]))
        self.wait_for_play_mode_set(playModeState, timeout)

    def play_and_wait(self, timeout=10):
        """
        Send play command and wait until zp is playing
        :param timeout:
        :return:
        """
        self._baseMuseClient.playback.play()
        self.wait_for_playback_state(playbackState=PlaybackState.PLAYING, timeout=timeout)

    def pause_and_wait(self, timeout=10):
        """
        Send pause command and wait until zp is paused
        :param timeout:
        :return:
        """
        self._baseMuseClient.playback.pause()
        self.wait_for_playback_state(playbackState=PlaybackState.PAUSED, timeout=timeout)
