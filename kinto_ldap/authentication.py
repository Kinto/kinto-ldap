import logging

from kinto.core import utils
from ldap import INVALID_CREDENTIALS, SCOPE_SUBTREE
from ldappool import BackendError
from pyramid import authentication as base_auth

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
    cache_key = utils.hmac_digest(hmac_secret, '{}:{}'.format(username, password))

    cache = request.registry.cache
    cache_result = cache.get(cache_key)

    bind_dn = settings.get('ldap.bind_dn')
    bind_password = settings.get('ldap.bind_password')

    if cache_result is None:
        cm = request.registry.ldap_cm

        # 0. Generate a search filter by combining the attribute and
        # filter provided in the ldap.fqn_filters directive with the
        # username passed by the HTTP client.
        base_dn = settings['ldap.base_dn']
        filters = settings['ldap.filters'].format(mail=username)

        # 1. Search for the user
        try:
            with cm.connection(bind_dn, bind_password) as conn:
                # import pdb; pdb.set_trace()
                results = conn.search_s(base_dn, SCOPE_SUBTREE, filters)
        except BackendError:
            logger.exception("LDAP error")
            return None

        if len(results) != 1:
            # If the search does not return exactly one entry, deny or decline access.
            return None

        dn, entry = results[0]
        user_dn = str(dn)

        # 2. Fetch the distinguished name of the entry retrieved from
        # the search and attempt to bind to the LDAP server using that
        # DN and the password passed by the HTTP client. If the bind
        # is unsuccessful, deny or decline access.
        try:
            with cm.connection(user_dn, password):
                cache.set(cache_key, "1", ttl=cache_ttl)
                return []
        except BackendError:
            logger.exception("LDAP error")
        except INVALID_CREDENTIALS:
            cache.set(cache_key, "0", ttl=cache_ttl)

    elif cache_result == "1":
        return []

    return None


class LDAPBasicAuthAuthenticationPolicy(base_auth.BasicAuthAuthenticationPolicy):
    """Basic auth with user credentials checked against an LDAP server."""
    def __init__(self, *args, **kwargs):
        super(LDAPBasicAuthAuthenticationPolicy, self).__init__(
            user_checker, *args, **kwargs)

    def effective_principals(self, request):
        # Bypass default Pyramid construction of principals because
        # Pyramid multiauth already adds userid, Authenticated and Everyone
        # principals.
        return []

    def _get_credentials(self, request):
        # Pyramid < 1.8
        policy = base_auth.BasicAuthAuthenticationPolicy
        if hasattr(policy, '_get_credentials'):  # pragma: no cover
            return policy._get_credentials(self, request)
        # Pyramid > 1.8
        return base_auth.extract_http_basic_credentials(request)  # pragma: no cover

    def unauthenticated_userid(self, request):
        credentials = self._get_credentials(request)
        if credentials:
            username, password = credentials

            return '%s' % username


def ldap_ping(request):
    """Verify if the LDAP server is ready."""
    settings = request.registry.settings
    bind_dn = settings.get('ldap.bind_dn')
    bind_password = settings.get('ldap.bind_password')
    base_dn = settings['ldap.base_dn']
    cm = request.registry.ldap_cm
    try:
        with cm.connection(bind_dn, bind_password) as conn:
            # Perform a dumb query
            filters = settings['ldap.filters'].format(mail="demo")
            conn.search_s(base_dn, SCOPE_SUBTREE, filters)
            ldap = True
    except Exception:
        logger.exception("Heartbeat Failure")
        ldap = False

    return ldap
