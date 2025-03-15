"""
ui_automator.py

Contains the UIAutomator class used for Android device control
via Mobly / snippet.
"""

import logging
from mobly.controllers import android_device
from mobly.controllers.android_device_lib import adb
from mobly import utils
from mobly.snippet import errors as snippet_errors

class UIAutomator:
    """Basic Android control support via Mobly/uiautomator/snippet."""
    def __init__(self, logger=None):
        self._logger = logger or logging.getLogger()
        self._connected_device = None

    def load_device(self):
        try:
            android_devices = android_device.get_all_instances()
            if not android_devices:
                raise ValueError('No Android device connected.')
            self._connected_device = android_devices[0]
            self._logger.info(f'Connected device: [{self._connected_device}]')
        except (FileNotFoundError, ValueError) as exc:
            self._logger.warning(f"Failed to load Android device: {str(exc)}")
            self._logger.info("Falling back to alternative method.")
            self._connected_device = None

    def connect_wireless(self, ip_address):
        try:
            self._connected_device = android_device.AndroidDevice(serial=ip_address)
            self._connected_device.adb.connect(ip_address)
            self._logger.info(f'Connected to device wirelessly: {ip_address}')
        except adb.AdbError as e:
            self._logger.warning(f"Failed to connect to {ip_address}: {str(e)}")
            self._logger.info("Skipping wireless connection.")
            self._connected_device = None

    def load_snippet(self):
        try:
            if not self._connected_device:
                raise ValueError('No Android device connected.')
            snippet_package = 'com.example.snippet'
            snippet_name = 'mbs'
            if not self._is_apk_installed(self._connected_device, snippet_package):
                self._install_apk(self._connected_device, self._get_snippet_apk_path())
            self._connected_device.load_snippet(snippet_name, snippet_package)
        except (ValueError, snippet_errors.ServerStartPreCheckError, snippet_errors.ServerStartError,
                snippet_errors.ProtocolError, android_device.SnippetError) as e:
            self._logger.warning(f"Failed to load snippet: {str(e)}")
            self._logger.info("Skipping snippet loading.")

    def _is_apk_installed(self, device, package_name):
        out = device.adb.shell(['pm', 'list', 'package'])
        return bool(utils.grep('^package:%s$' % package_name, out))

    def _install_apk(self, device, apk_path):
        device.adb.install(['-r', '-g', apk_path])

    def _get_snippet_apk_path(self):
        return '/path/to/your/snippet.apk'
