from base_helper import baseNamespaceHelper
from urlparse import urlparse


SAMPLE_AUDIOCLIP="https://stream-media.loc.gov/afc/tendingcommons/afc1999008_crf_mha041015.mp3"


class audioclipNamespaceHelpers(baseNamespaceHelper):
    """
    Helper functions that are mainly orientated towards the audioclip namespace commands
    """
    def __init__(self, restClient):
        super(audioclipNamespaceHelpers, self).__init__(restClient=restClient)

    def play_clip_from_url(self, url=SAMPLE_AUDIOCLIP):
        """
        Plays a clip from a given url endpoint with required parameters autofilled

        :param str url: Url of audio file
        :return str: ID of clip. Can be used to cancel via cancelAudioClip(id) command
        """
        return self._baseMuseClient.audioClip.loadAudioClip(name=urlparse(url).netloc,  # make the url domain the name
                                                            appId="muse_rest_client",
                                                            streamUrl=url)["id"]

