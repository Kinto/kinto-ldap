CHANGELOG
=========

This document describes changes between each past release.


0.2.1 (2016-11-03)
------------------

**Bug fixes**

- Fix heartbeat that would always return False


0.2.0 (2016-11-02)
------------------

- Set default value for ``multiauth.policy.ldap.use`` (fixes #3)
- Add the plugin version in the capability.

**New features**

- Add connection pool settings (fixes #10)

**Bug fixes**

- Fix heartbeat when server is unreachable (fixes #8)
- Returns None and log exception if LDAP backend cannot be reached (fixes #9)

0.1.0 (2016-06-27)
------------------

- Basic Auth Authentication for LDAP.
