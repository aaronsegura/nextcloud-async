# nextcloud-async
## Asynchronous Nextcloud Client

This module provides an asyncio-friendly interface to Nextcloud.

### Covered APIs
* App Management

* File Management
* Group Management
* GroupFolders
* LDAP Configuration
* Login Flow v2
* Maps
* Notifications
* Remote Wipe
* Share (except Federated shares)
* Sharee
* Status
* Talk/spreed
* User Management


###s To Do
* Reaction
* User Preferences
* Federated Shares
* Cookbook
* Passwords
* Notes
* Deck
* Calendar CalDAV
* Tasks CalDAV
* Contacts CardDAV
* Comments

If you know of any APIs missing from this list, please open an issue at
https://github.com/aaronsegura/nextcloud-async/issues with a link to
the documentation so it can be added.  This project aims to eventually
cover any provided by Nextcloud and commonly used Nextcloud apps.

### Example Usage
    import httpx
    import asyncio
    from nextcloud_async import NextcloudClient
    from nextcloud_async.api import Apps

    nc = NextcloudClient(
        http_client=httpx.AsyncClient(timeout=30),
        endpoint='http://localhost:8181',
        user='admin',
        password='admin')

    async def main():
        apps = Apps(nc)
        capabilities = await apps.api.get_capabilities()
        if 'groupfolders' not in capabilities['capabilities']:
            print('Enabling GroupFolders')
            await apps.enable('groupfolders')
        else:
            print('GroupFolders already enabled.')

        response = await apps.get('groupfolders')
        print(f'{response['name']} v{response['version']}: {response['summary']}')

    if __name__ == "__main__":
        asyncio.run(main())

----
This project is not endorsed or recognized in any way by the Nextcloud project.
