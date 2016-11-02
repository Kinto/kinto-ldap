import unittest

import mock

import kinto.core
from pyramid.exceptions import ConfigurationError
from pyramid import testing

from kinto_ldap import includeme


class IncludeMeTest(unittest.TestCase):
    def test_include_fails_if_kinto_was_not_initialized(self):
        config = testing.setUp()
        with self.assertRaises(ConfigurationError):
            config.include(includeme)

    def test_settings_are_filled_with_defaults(self):
        config = testing.setUp()
        kinto.core.initialize(config, '0.0.1')
        config.include(includeme)
        settings = config.get_settings()
        self.assertIsNotNone(settings.get('ldap.cache_ttl_seconds'))

    def test_a_heartbeat_is_registered_at_oauth(self):
        config = testing.setUp()
        kinto.core.initialize(config, '0.0.1')
        config.registry.heartbeats = {}
        config.include(includeme)
        self.assertIsNotNone(config.registry.heartbeats.get('ldap'))

    def test_connection_manager_is_instantiated_with_settings(self):
        config = testing.setUp()
        kinto.core.initialize(config, '0.0.1')
        with mock.patch('kinto_ldap.ConnectionManager') as mocked:
            includeme(config)
            mocked.assert_called_with(retry_delay=0.1,
                                      retry_max=3,
                                      size=10,
                                      timeout=30,
                                      uri='ldap://ldap.db.scl3.mozilla.com')