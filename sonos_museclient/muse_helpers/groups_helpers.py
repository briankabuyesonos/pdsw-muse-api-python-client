from sonos.services.common import wait_until_true
from base_helper import baseNamespaceHelper


class groupsNamespaceHelpers(baseNamespaceHelper):
    """
    Helper functions that are mainly orientated towards the groups namespace commands
    """
    def __init__(self, restClient):
        super(groupsNamespaceHelpers, self).__init__(restClient=restClient)

    def get_number_groups_in_hh(self):
        """
        Returns the number of groups in the ZP's household
        :return:
        """
        return len(self._baseMuseClient.groups.getGroups()["groups"])

    def get_zone_group_object(self, playerId):
        """
        Return the group object that contains the provided playerId
        :param playerId:
        :return:
        """
        for group in self._baseMuseClient.groups.getGroups()["groups"]:
            if playerId in group["playerIds"]:
                return group
        else:
            return None

    def is_group_coordinator_local(self, timeout=60):
        """
        Returns whether the ZP is the GC of the group its in
        :param timeout:
        :return:
        """
        wait_until_true(lambda: self.get_zone_group_object(self._baseMuseClient.uuid) is not None,
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="Did not find the zp's group object")
        return self.get_zone_group_object(self._baseMuseClient.uuid)["coordinatorId"] == self._baseMuseClient.uuid

    def is_group_member_to_zone(self, zone, timeout=60):
        """
        Returns whether the ZP is a group member of zone's group
        :param zone:
        :param timeout:
        :return:
        """
        wait_until_true(lambda: self.get_zone_group_object(self._baseMuseClient.uuid) is not None,
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="Did not find the zp's group object")
        return self.get_zone_group_object(zone.raw_udn)["coordinatorId"] != self._baseMuseClient.uuid and \
               self._baseMuseClient._uuid in self.get_zone_group_object(zone.raw_udn)["playerIds"]

    def join_group(self, zone, timeout=60):
        """
        Add ZP to zone's group
        :param zone:
        :param timeout:
        :return:
        """
        numGroups = self.get_number_groups_in_hh()
        zone.muse_rest.groups.modifyGroupMembers(playerIdsToAdd=[self._baseMuseClient._uuid], playerIdsToRemove=[])

        # Wait until number of groups in the household has decreased by one
        wait_until_true(lambda: self.get_number_groups_in_hh() == numGroups-1,
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="Number of groups in household did not decrease by one")

        # Wait until the ZP is a group member in zone's group
        wait_until_true(lambda: self.is_group_member_to_zone(zone),
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="Did not find zp's playerId in zone's group's playerId list")

        # Verify zone is still the GC of the group its in
        wait_until_true(lambda: (self.get_zone_group_object(zone.raw_udn) is not None and
                                 self.get_zone_group_object(zone.raw_udn)["coordinatorId"] == zone.raw_udn),
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="Zone's playerId is not its group's GC")

    def leave_group(self, timeout=60):
        """
        Make the ZP leave whatever group its in
        :param timeout:
        :return:
        """
        self._baseMuseClient.groups.createGroup(playerIds=[self._baseMuseClient._uuid])

        # Wait until the ZP's group has only 1 playerId
        wait_until_true(lambda: (self.get_zone_group_object(self._baseMuseClient._uuid) is not None and
                                 len(self.get_zone_group_object(self._baseMuseClient._uuid)["playerIds"]) == 1),
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="Found more then one playerId in zp's group's playerId list")

        # Wait until the ZP is the GC of its own group
        wait_until_true(lambda: self.is_group_coordinator_local(),
                        timeout_seconds=timeout, iteration_delay=1,
                        reason="zp's group's GC is not zp's playerId")
