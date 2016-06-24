from ldappool import ConnectionManager
from pyramid.exceptions import ConfigurationError

from kinto_ldap.authentication import ldap_ping


DEFAULT_SETTINGS = {
    'ldap.cache_ttl_seconds': 30,
    'ldap.endpoint': 'ldap://ldap.db.scl3.mozilla.com',
    'ldap.fqn': 'mail={mail},o=com,dc=mozilla',
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

    # Register heartbeat to ping the LDAP server.
    config.registry.heartbeats['ldap'] = ldap_ping
    config.registry.ldap_cm = ConnectionManager(settings['ldap.endpoint'])
