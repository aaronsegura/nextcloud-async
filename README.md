# nextcloud-async
## Asynchronous Nextcloud Client

This module provides an asyncio-friendly interface to public Nextcloud APIs.

### Covered APIs
* File Management API
* User Management API
* Group Management API
* GroupFolders API
* App Management API
* LDAP Configuration API
* Status API
* Share API (except Federated shares)
* Talk/spreed API
* Notifications API
* Login Flow v2 API
* Remote Wipe API
* Maps API

### APIs To Do
* Sharee API
* Reaction API
* User Preferences API
* Federated Shares API
* Cookbook API
* Passwords API
* Notes API
* Deck API
* Calendar CalDAV API
* Tasks CalDAV API
* Contacts CardDAV API

If you know of any APIs missing from this list, please open an issue at
https://github.com/aaronsegura/nextcloud-async/issues with a link to
the API documentation so it can be added.  This project aims to eventually
cover any API provided by Nextcloud and commonly used Nextcloud apps.

### Example Usage
    import httpx
    import asyncio
    from nextcloud_async import NextcloudAsync

    nca = NextcloudAsync(
        client=httpx.AsyncClient(),
        endpoint='http://localhost:8181',
        user='user',
        password='password')

    async def main():
        users = await nca.get_users()
        tasks = [nca.get_user(user) for user in users]
        results = await asyncio.gather(*tasks)
        for user_info in results:
            print(user_info)

    if __name__ == "__main__":
        asyncio.run(main())

----
This project is not endorsed or recognized in any way by the Nextcloud
project.
