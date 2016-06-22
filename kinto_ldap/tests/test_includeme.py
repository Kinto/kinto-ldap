import kinto.core
from pyramid.exceptions import ConfigurationError
from pyramid import testing

from kinto_ldap import includeme
from . import unittest


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
