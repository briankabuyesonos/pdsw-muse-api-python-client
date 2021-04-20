import pytest
import random
from sonos.services.common import wait_until_true
from sonos.client.zp_logger import ZpLogger, Logs
from sonos.client.zone_player import PLAYBACK_DEVICES
import inspect
import re
from collections import Iterable


class device_manager(object):
    """
    Object to keep track all the Sonos devices a test case might use
    """
    def __init__(self, all_devices, override_dut=None):
        """
        Initialize the class and default values
        :param all_devices:
        """
        # Main test case dut
        self._zp = None
        # All devices the test case used
        self._test_devices = []

        # Pool of Sonos devices available for use on the testbed
        self._all_devices = all_devices
        assert all_devices is not None, \
            "all_devices should not be None"

        self.loggers = {}

        self.override_dut = override_dut

    @property
    def zp(self):
        """
        this should be the main dut for a test case
        :return:
        """
        return self._zp

    @zp.setter
    def zp(self, zp):
        """
        self.zp setter
        :param zp:
        :return:
        """
        self._zp = zp

    @property
    def test_devices(self):
        """
        this should be all the zps used in a test, which should include self.zp
        :return:
        """
        return self._test_devices

    @test_devices.setter
    def test_devices(self, test_devices):
        """
        self.test_devices setter
        :param test_devices:
        :return:
        """
        self._test_devices = test_devices

    @property
    def all_playback_devices(self):
        """
        this should be the pool of available playback devices on a testbed, maintained for backwards
        compat reasons
        :return:
        """
        return [d for d in self._all_devices if d.modelNumber in PLAYBACK_DEVICES]

    @property
    def all_devices(self):
        """
        this should be the pool of all devices on a testbed
        :return:
        """
        return self._all_devices

    def get_test_device(self, device_filter=PLAYBACK_DEVICES, fail_on_none=True, tracked_logs=None):
        """
        Get a ZP from the pool of all devices based on a selection filter
        :param device_filter: Either a selection of acceptable device types or a custom lambda selector
        :param fail_on_none: If no device matching given criteria found, determines wheter device fails (AssertionError)
                             or skips the test
        :param tracked_logs: Logs to monitor on selected zp. See sonos.client.zp_logger.Logs class
        :return:
        """
        # Filter out already used devices
        unused_zps = [d for d in self.all_devices if d not in self.test_devices]
        subset_zps = unused_zps
        selected_zp = None
        filterStr = device_filter

        if device_filter is not None:
            # Allow user to pass in custom lambda picker function
            if callable(device_filter):
                # Save the eventFilter lambda as a string
                try:
                    rawEventFilterString = ' '.join([l.strip() for l in inspect.getsource(device_filter).splitlines()])
                    filterStr = rawEventFilterString
                except Exception:
                    filterStr = None
                subset_zps = [d for d in subset_zps if device_filter(d)]
            else:
                if not isinstance(device_filter, Iterable):
                    device_filter = [device_filter]
                subset_zps = [d for d in subset_zps if d.modelNumber in device_filter]

        if len(subset_zps) > 0:
            selected_zp = random.choice(subset_zps)

            # Add logging to zp
            self.add_logging(zp=selected_zp, tracked_logs=tracked_logs)

            return selected_zp
        elif not fail_on_none or self.override_dut is not None:
            pytest.skip("Sonos devices filtered by <{}> not found in available devices: \n{}".format(
                filterStr, "\n".join(map(str, unused_zps))))
            return None
        else:
            assert len(subset_zps) > 0, \
                "Sonos devices filtered by \n<{}> \nnot found in available devices: \n{}".format(
                    filterStr, "\n".join(map(str, unused_zps)))

    def get_primary_dut(self, device_filter=PLAYBACK_DEVICES, fail_on_none=True, tracked_logs=None):
        """
        Find a suitable zp to act as primary dut, assign to self.zp
         and add it to the test_devices list.
        :param device_filter: Either a selection of acceptable device types or a custom lambda selector
        :param fail_on_none: If no device matching given criteria found, determines wheter device fails (AssertionError)
                             or skips the test
        :param tracked_logs: Logs to monitor on selected zp. See sonos.client.zp_logger.Logs class
        :return:
        """
        # Reset internal attributes
        self.test_devices = []
        self.reset_loggers()

        # Set the device filter to find the desired player if override_dut is set
        if self.override_dut is not None:
            device_filter = lambda z: self.override_dut in z.muse_rest.uuid

        self.zp = self.get_another_device(device_filter, fail_on_none, tracked_logs)
        return self.zp

    def get_another_device(self, device_filter=PLAYBACK_DEVICES, fail_on_none=True, tracked_logs=None):
        """
        If the test cases needs additional ZPs, use this method to get those ZPs since it
        will also add them to the test_devices list.
        :param device_filter: Either a selection of acceptable device types or a custom lambda selector
        :param fail_on_none: If no device matching given criteria found, determines wheter device fails (AssertionError)
                             or skips the test
        :param tracked_logs: Logs to monitor on selected zp. See sonos.client.zp_logger.Logs class
        :return:
        """
        zp = self.get_test_device(device_filter, fail_on_none, tracked_logs)
        self.test_devices.append(zp)
        return zp

    def get_more_devices(self, num, group=False, device_filter=PLAYBACK_DEVICES, fail_on_none=True, tracked_logs=None):
        """
        This method grabs n number of additional devices and groups them together if desired

        :param num: Number of additional devices to get
        :param group: Should group them together, with main zp as gc
        :param device_filter: Either a selection of acceptable device types or a custom lambda selector
        :param fail_on_none: If no device matching given criteria found, determines wheter device fails (AssertionError)
                             or skips the test
        :param tracked_logs: Logs to monitor on selected zp. See sonos.client.zp_logger.Logs class
        :return:
        """
        new_zps = []
        for _ in range(num):
            new = self.get_another_device(device_filter, fail_on_none, tracked_logs)
            new_zps.append(new)

            if group:
                new.AVTransport.join_group(self.zp)

        return new_zps

    def zp_cleanup(self, zp, unbond=True, ungroup=True, clear_avt=True, lower_volume=True, clear_queue=True):
        """
        Cleans up the zp to return it to a ready to test state
        :param zp:
        :return:
        """
        if unbond and hasattr(zp, "DeviceProperties") and (zp.is_bonded() or zp.is_satellite()):
            # Cleanup bonded configs if bonded
            zp.DeviceProperties.cleanup_bonded_configuration()
            wait_until_true(lambda: (not zp.is_bonded() and not zp.is_satellite()),
                            timeout_seconds=10, iteration_delay=1,
                            reason="ZP should be unbonded")

        if ungroup and hasattr(zp, "GroupManagement") and hasattr(zp, "AVTransport") and\
                not zp.GroupManagement.is_group_coordinator_local():
            # Cleanup grouped configs if grouped
            zp.AVTransport.BecomeCoordinatorOfStandaloneGroup()
            wait_until_true(lambda: (zp.GroupManagement.is_group_coordinator_local()),
                            timeout_seconds=10, iteration_delay=1,
                            reason="ZP should be ungrouped")

        if clear_avt and hasattr(zp, "AVTransport") and \
                (zp.AVTransport.is_playing() or zp.AVTransport.is_paused()):
            if ungroup or zp.GroupManagement.is_group_coordinator_local():  # Clearing transport will ungroup GMs
                # Clear the avt if the zp is playing or paused
                zp.AVTransport.SetAVTransportURI_and_wait("", "")
                wait_until_true(lambda: (not zp.AVTransport.is_playing() and not zp.AVTransport.is_paused()),
                                timeout_seconds=10, iteration_delay=1,
                                reason="ZP should be stopped")

        if lower_volume and hasattr(zp, "RenderingControl"):
            zp.RenderingControl.SetVolume(10)

        if clear_queue and hasattr(zp, "AVTransport") and\
                zp.AVTransport.get_number_of_tracks_in_queue() > 0:
            zp.AVTransport.clear_queue()

    def zp_cleanup_all_test_devices(self, unbond=True, ungroup=True, clear_avt=True, lower_volume=True):
        """
        Cleanup all the zps in the test_devices list
        :return:
        """
        for zp in self.test_devices:
            if zp is not None:
                self.zp_cleanup(zp, unbond=unbond, ungroup=ungroup,
                                clear_avt=clear_avt, lower_volume=lower_volume)

    def reset_manager(self, unbond=True, ungroup=True, clear_avt=True, lower_volume=True):
        """
        Cleanup all zps in the test_devices list and reset the zp and test_devices properties
        :return:
        """
        self.zp_cleanup_all_test_devices(unbond=unbond, ungroup=ungroup,
                                         clear_avt=clear_avt, lower_volume=lower_volume)
        self.zp = None
        self.test_devices = []

    def add_logging(self, zp, tracked_logs=None, cq_control=None):
        """
        Creates a logger if one does not already existF, and starts any new requested logs
        :param zp:
        :param tracked_logs:
        :param cq_control:
        :return:
        """
        if zp is not None:
            if zp not in self.loggers:
                self.loggers[zp] = ZpLogger(zp=zp, cq_control=cq_control)

            if cq_control is not None:
                self.loggers[zp].cq_control = cq_control

            if tracked_logs is not None and Logs.CLOUD_QUEUE in tracked_logs and \
                    self.loggers[zp].cq_control is None:
                raise ValueError("Cannot start cloudqueue logging without first providing a cq object")

            if tracked_logs is not None:
                self.loggers[zp].init(tracked_logs)
            else:
                self.loggers[zp].init_all()

        return self.loggers[zp]

    def print_logs(self, logs_to_print=None, cleanup_after_print=True, do_not_print_zps=[]):
        """
        Dumps all active logs for all zps in `self.loggers`
        :param logs_to_print: Logs to print. If None, prints everything active
        :param cleanup_after_print: cleans up log states for the next run
        :param do_not_print_zps: list of zps to not print logs for. Used for confusing module scoped zp handling
        :return:
        """
        # Filter out ignored ZPs
        zps = [zp for zp in self.loggers if zp not in do_not_print_zps]
        zps = sorted(zps, key=lambda zp: self.loggers[zp].tag)  # Order by tags

        for zp in zps:  # only print for devices which are actively used
            if logs_to_print is None:
                self.loggers[zp].print_active_logs()
            else:
                self.loggers[zp].print_logs(logs_to_print)

        if cleanup_after_print:
            self.reset_loggers()

    def reset_loggers(self):
        """
        Cleans up any logs and resets logger dict to empty
        :return:
        """
        for zp in self.loggers:
            self.loggers[zp].cleanup()
        self.loggers = {}

    def check_backtraces(self, only_used_devices=False):
        """
        Checks devices for backtraces
        :param only_used_devices: Only check devices that were used in the course of the test
        :return: dict of zp key with backtrace string value
        """
        zps = self.all_devices

        if only_used_devices:
            # Use loggers because there is a better chance they haven't been deleted yet
            zps = [zp for zp in self.loggers]

        return [zp for zp in zps if zp.cli.has_backtrace()]

    def check_watchdogs(self, only_used_devices=False):
        """
        Check devices for watchdogs
        :param only_used_devices:
        :return:
        """
        zps = self.all_devices

        if only_used_devices:
            # Use loggers because there is a better chance they haven't been deleted yet
            zps = [zp for zp in self.loggers]

        return [zp for zp in zps if zp.cli.has_watchdog()]

    @staticmethod
    def disconnect_testbed(msg):
        """
        Take the testbed offline
        :return:
        """
        from sonos.testbed.testrunner_properties import (
            get_node_name,
            get_automation_username,
            get_automation_password,
            running_on_jenkins_testbed)
        if running_on_jenkins_testbed():
            from jenkins.disable_node import DisableTestbed

            DisableTestbed(get_node_name(), get_automation_username(), get_automation_password(),
                           msg).set_node_offline()
