import unittest

import mock

import kinto.core
import webtest
from kinto.core.utils import random_bytes_hex
from pyramid.config import Configurator

from kinto_ldap import __version__ as ldap_version


def get_request_class(prefix):

    class PrefixedRequestClass(webtest.app.TestRequest):

        @classmethod
        def blank(cls, path, *args, **kwargs):
            path = '/%s%s' % (prefix, path)
            return webtest.app.TestRequest.blank(path, *args, **kwargs)

    return PrefixedRequestClass


class BaseWebTest(object):
    """Base Web Test to test your cornice service.

    It setups the database before each test and delete it after.
    """

    api_prefix = "v0"

    def __init__(self, *args, **kwargs):
        super(BaseWebTest, self).__init__(*args, **kwargs)
        self.app = self._get_test_app()
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _get_test_app(self, settings=None):
        config = self._get_app_config(settings)
        wsgi_app = config.make_wsgi_app()
        app = webtest.TestApp(wsgi_app)
        app.RequestClass = get_request_class(self.api_prefix)
        return app

    def _get_app_config(self, settings=None):
        config = Configurator(settings=self.get_app_settings(settings))
        kinto.core.initialize(config, version='0.0.1')
        return config

    def get_app_settings(self, additional_settings=None):
        settings = kinto.core.DEFAULT_SETTINGS.copy()
        settings['includes'] = 'kinto_ldap'
        settings['multiauth.policies'] = 'ldap'
        authn = 'kinto_ldap.authentication.LDAPBasicAuthAuthenticationPolicy'
        settings['multiauth.policy.ldap.use'] = authn
        settings['cache_backend'] = 'kinto.core.cache.memory'
        settings['cache_backend'] = 'kinto.core.cache.memory'
        settings['userid_hmac_secret'] = random_bytes_hex(16)

        if additional_settings is not None:
            settings.update(additional_settings)
        return settings


class CapabilityTestView(BaseWebTest, unittest.TestCase):

    def test_ldap_capability(self, additional_settings=None):
        resp = self.app.get('/')
        capabilities = resp.json['capabilities']
        self.assertIn('ldap', capabilities)
        expected = {
            "version": ldap_version,
            "url": "https://github.com/mozilla-services/kinto-ldap",
            "description": "Basic Auth user are validated against an "
                           "LDAP server."
        }
        self.assertEqual(expected, capabilities['ldap'])


class HeartbeatTest(BaseWebTest, unittest.TestCase):

    def get_app_settings(self, extras=None):
        settings = super(HeartbeatTest, self).get_app_settings(extras)
        settings['ldap.pool_timeout'] = '1'
        return settings

    def test_heartbeat_returns_false_if_unreachable(self):
        unreachable = 'ldap://ldap.with.unreachable.server.com'
        app = self._get_test_app(settings={'ldap.endpoint': unreachable})
        resp = app.get('/__heartbeat__', status=503)
        heartbeat = resp.json['ldap']
        self.assertFalse(heartbeat)

    def test_heartbeat_returns_true_if_test_credentials_are_valid(self):
        self.app.app.registry.ldap_cm = mock.MagicMock()
        resp = self.app.get('/__heartbeat__')
        heartbeat = resp.json['ldap']
        self.assertTrue(heartbeat)
