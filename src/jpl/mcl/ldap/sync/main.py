# encoding: utf-8

import click, sys, ldap, getpass


# Defaults
URL        = u'ldaps://edrn.jpl.nasa.gov'
MANAGER_DN = u'uid=admin,ou=system'
USER_BASE  = u'ou=users,o=MCL'
SCOPE      = u'one'
USER_CLASS = u'inetOrgPerson'
GROUP_DN   = u'cn=All MCL,ou=groups,o=MCL'


# From command-line to ldap constants
_scopes = {
    'base': ldap.SCOPE_BASE,
    'one': ldap.SCOPE_ONELEVEL,
    'sub': ldap.SCOPE_SUBTREE
}


@click.command()
@click.option('--url', default=URL, help=u'URL to the LDAP server')
@click.option('--manager', default=MANAGER_DN, help=u'DN of the LDAP admin account')
@click.option('--password', help=u'Password of the LDAP admin account; if not given you will be prompted')
@click.option('--userbase', default=USER_BASE, help=u'Base DN where users are found')
@click.option('--scope', default=SCOPE, help=u'Search scope to find users', type=click.Choice(['base', 'one', 'sub']))
@click.option('--userclass', default=USER_CLASS, help=u'Object class to determine users')
@click.option('--group', default=GROUP_DN, help=u'DN of group to update')
def main(url, manager, password, userbase, scope, userclass, group):
    if not password:
        password = getpass.getpass()
    connection = ldap.initialize(url)
    connection.simple_bind_s(manager, password)
    allUsers = connection.search_s(userbase, _scopes[scope], u'(objectClass={})'.format(userclass), [], attrsonly=1)
    allUsers = set([i[0] for i in allUsers])
    currentMembers = connection.search_s(group, ldap.SCOPE_BASE, u'(objectClass=*)', ['uniqueMember'])
    currentMembers = set(currentMembers[0][1]['uniqueMember'])
    usersToAdd = allUsers - currentMembers
    membersToRemove = currentMembers - allUsers
    if usersToAdd:
        connection.modify_s(group, [(ldap.MOD_ADD, 'uniqueMember', list(usersToAdd))])
    if membersToRemove:
        connection.modify_s(group, [(ldap.MOD_DELETE, 'uniqueMember', list(membersToRemove))])
    return True


if __name__ == '__main__':
    sys.exit(0 if main() else -1)
