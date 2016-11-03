import base64
import ldap
import unittest
import time

import mock
from ldappool import BackendError

from kinto.core.cache import memory as memory_backend
from kinto.core.testing import DummyRequest

from kinto_ldap import authentication, DEFAULT_SETTINGS


class LDAPBasicAuthAuthenticationPolicyTest(unittest.TestCase):
    def setUp(self):
        self.policy = authentication.LDAPBasicAuthAuthenticationPolicy()
        self.backend = memory_backend.Cache(cache_prefix="tests")

        self.request = DummyRequest()
        self.request.registry.cache = self.backend
        self.request.registry.ldap_cm = mock.MagicMock()
        settings = DEFAULT_SETTINGS.copy()
        settings['userid_hmac_secret'] = 'abcdef'
        settings['ldap.cache_ttl_seconds'] = 0.01
        self.request.registry.settings = settings
        self.request.headers['Authorization'] = (
            'Basic ' + base64.b64encode(b'username:password').decode('utf-8'))

    def tearDown(self):
        self.backend.flush()

    def test_returns_none_if_server_is_unreachable(self):
        error = BackendError("unreachable", backend=None)
        self.request.registry.ldap_cm.connection \
            .return_value.__enter__.side_effect = error
        user_id = self.policy.authenticated_userid(self.request)
        self.assertIsNone(user_id)

    def test_returns_none_if_authorization_header_is_missing(self):
        self.request.headers.pop('Authorization')
        user_id = self.policy.authenticated_userid(self.request)
        self.assertIsNone(user_id)

    def test_returns_none_if_token_is_malformed(self):
        self.request.headers['Authorization'] = 'Basicabcd'
        user_id = self.policy.authenticated_userid(self.request)
        self.assertIsNone(user_id)

    def test_returns_none_if_token_is_unknown(self):
        self.request.headers['Authorization'] = 'Basic foo'
        user_id = self.policy.authenticated_userid(self.request)
        self.assertIsNone(user_id)

    def test_returns_ldap_userid(self):
        mocked = mock.MagicMock()
        self.request.registry.ldap_cm.connection \
            .return_value.__enter__.return_value = mocked

        user_id = self.policy.authenticated_userid(self.request)
        self.assertEqual("username", user_id)

    def test_auth_verification_uses_cache(self):
        mocked = mock.MagicMock()
        self.request.registry.ldap_cm.connection \
            .return_value.__enter__.return_value = mocked

        self.policy.authenticated_userid(self.request)
        self.policy.authenticated_userid(self.request)
        self.assertEqual(
            1, self.request.registry.ldap_cm.connection.call_count)

    def test_auth_verification_cache_has_ttl(self):
        mocked = mock.MagicMock()
        self.request.registry.ldap_cm.connection \
            .return_value.__enter__.return_value = mocked

        self.policy.authenticated_userid(self.request)
        time.sleep(0.02)
        self.policy.authenticated_userid(self.request)
        self.assertEqual(
            2, self.request.registry.ldap_cm.connection.call_count)

    def test_returns_none_if_user_password_mismatch(self):
        self.request.registry.ldap_cm.connection \
            .return_value.__enter__.side_effect = ldap.INVALID_CREDENTIALS()
        self.assertIsNone(self.policy.authenticated_userid(self.request))

    def test_forget_uses_realm(self):
        policy = authentication.LDAPBasicAuthAuthenticationPolicy(realm='Who')
        headers = policy.forget(self.request)
        self.assertEqual(headers[0],
                         ('WWW-Authenticate', 'Basic realm="Who"'))
