kinto-ldap
==========

|travis| |master-coverage|

.. |master-coverage| image::
    https://coveralls.io/repos/Kinto/kinto-ldap/badge.svg?branch=master
    :alt: Coverage
    :target: https://coveralls.io/r/Kinto/kinto-ldap

.. |travis| image:: https://travis-ci.org/Kinto/kinto-ldap.svg?branch=master
    :target: https://travis-ci.org/Kinto/kinto-ldap


Validate Basic Auth provided user login and password with an LDAP server.


Dependencies
------------

Before installing you will need the following system dependencies::

    sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev


Installation
------------

Install the Python package:

::

    pip install kinto-ldap


Include the package in the project configuration:

::

    kinto.includes = kinto_ldap

And configure authentication policy using `pyramid_multiauth
<https://github.com/mozilla-services/pyramid_multiauth#deployment-settings>`_ formalism:

::

    multiauth.policies = ldap
    multiauth.policy.ldap.use = kinto_ldap.authentication.LDAPBasicAuthAuthenticationPolicy

By default, it will rely on the cache configured in *Kinto*.


Configuration
-------------

Fill those settings with the values obtained during the application registration:

::

    # ldap.cache_ttl_seconds = 30
    # ldap.endpoint = ldap://ldap.prod.mozaws.net
    # ldap.fqn = "uid={uid},ou=users,dc=mozilla"


If necessary, override default values for authentication policy:

::

    # multiauth.policy.ldap.realm = Realm
