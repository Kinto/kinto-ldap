import logging

from kinto.core import utils
from ldap import INVALID_CREDENTIALS
from pyramid.authentication import BasicAuthAuthenticationPolicy

logger = logging.getLogger(__name__)


def user_checker(username, password, request):
    """LDAP user_checker
    Let you validate your Basic Auth users to a configured LDAP server.

    Use it like that::

        config = Configurator(
              authentication_policy=BasicAuthenticationPolicy(check=user_checker))
    """
    settings = request.registry.settings
    cache_ttl = settings['ldap.cache_ttl_seconds']
    hmac_secret = settings['userid_hmac_secret']
    cache_key = utils.hmac_digest(hmac_secret, '%s:%s' % (username, password))

    cache = request.registry.cache
    cache_result = cache.get(cache_key)

    ldap_fqn = settings['ldap.fqn']

    if cache_result is None:
        cm = request.registry.ldap_cm

        try:
            with cm.connection(ldap_fqn.format(mail=username), password):
                cache.set(cache_key, "1", ttl=cache_ttl)
                return []
        except INVALID_CREDENTIALS:
            cache.set(cache_key, "0", ttl=cache_ttl)

    elif cache_result == "1":
        return []

    return None


class LDAPBasicAuthAuthenticationPolicy(BasicAuthAuthenticationPolicy):
    """Basic auth with user credentials checked against an LDAP server."""
    def __init__(self, *args, **kwargs):
        super(LDAPBasicAuthAuthenticationPolicy, self).__init__(
            user_checker, *args, **kwargs)

    def unauthenticated_userid(self, request):
        credentials = self._get_credentials(request)
        if credentials:
            username, password = credentials

            return '%s' % username


def ldap_ping(request):
    """Verify if the LDAP server is ready."""
    cm = request.registry.ldap_cm
    try:
        with cm.connection():
            ldap = True
    except Exception:
        logger.exception("Heartbeat Failure")
        ldap = False

    return ldap
