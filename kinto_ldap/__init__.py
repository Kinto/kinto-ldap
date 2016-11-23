import pkg_resources

from ldappool import ConnectionManager
from pyramid.exceptions import ConfigurationError

from kinto_ldap.authentication import ldap_ping

#: Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version


DEFAULT_SETTINGS = {
    'multiauth.policy.ldap.use': ('kinto_ldap.authentication.'
                                  'LDAPBasicAuthAuthenticationPolicy'),
    'ldap.cache_ttl_seconds': 30,
    'ldap.endpoint': 'ldap://ldap.db.scl3.mozilla.com',
    'ldap.base_dn': 'dc=mozilla',
    'ldap.filters': '(mail={mail})',
    'ldap.pool_size': 10,
    'ldap.pool_retry_max': 3,
    'ldap.pool_retry_delay': .1,
    'ldap.pool_timeout': 30,
}


def includeme(config):
    if not hasattr(config.registry, 'heartbeats'):
        message = ('kinto-ldap should be included once Kinto is initialized'
                   ' . Use setting ``kinto.includes`` instead of '
                   '``pyramid.includes`` or include it manually.')
        raise ConfigurationError(message)

    settings = config.get_settings()

    defaults = {k: v for k, v in DEFAULT_SETTINGS.items() if k not in settings}
    config.add_settings(defaults)
    config.add_api_capability(
        "ldap", version=__version__,
        description="Basic Auth user are validated against an LDAP server.",
        url="https://github.com/mozilla-services/kinto-ldap")

    try:
        settings['ldap.filters'].format(mail='test')
    except KeyError:
        msg = "ldap.filters should take a 'mail' argument only, got: %r" % settings['ldap.filters']
        raise ConfigurationError(msg)
    else:
        if settings['ldap.filters'].format(mail='test') == settings['ldap.filters']:
            msg = "ldap.filters should take a 'mail' argument, got: %r" % settings['ldap.filters']
            raise ConfigurationError(msg)

    # Register heartbeat to ping the LDAP server.
    config.registry.heartbeats['ldap'] = ldap_ping

    # LDAP pool connection manager
    conn_options = dict(uri=settings['ldap.endpoint'],
                        size=int(settings['ldap.pool_size']),
                        retry_max=int(settings['ldap.pool_retry_max']),
                        retry_delay=float(settings['ldap.pool_retry_delay']),
                        timeout=int(settings['ldap.pool_timeout']))
    config.registry.ldap_cm = ConnectionManager(**conn_options)
