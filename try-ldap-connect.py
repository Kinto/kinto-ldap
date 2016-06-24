from ldappool import ConnectionManager
from getpass import getpass

LDAP_ENDPOINT = "ldap://ldap.db.scl3.mozilla.com"
USERNAME = "USER@mozilla.com"
FQN = "mail={mail},o=com,dc=mozilla"

password = getpass('Please enter a password for %s: ' % USERNAME)

cm = ConnectionManager(LDAP_ENDPOINT)

with cm.connection() as conn:
    conn.bind(FQN.format(mail=USERNAME), password)
    print("Connected as %s" % USERNAME)
