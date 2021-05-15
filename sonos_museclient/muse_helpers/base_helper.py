class baseNamespaceHelper(object):
    def __init__(self, restClient):
        """
        Set the internal instance of the muse rest client.
        We use the whole client instead of the respective namespace client as to not limit the available commands
        to just that namespace.
        :param restClient: instance of the MuseRestClient class
        """
        self._baseMuseClient = restClient
