Quickstart
##########

Your first step in getting started is to import and configure
the **NextcloudClient** object:

    .. code-block:: python

        from nextcloud_async import NextcloudClient

        client = NextcloudClient(
            user='user',
            password='password',
            endpoint='https://yourcloud.com',
            user_agent='optional-user-agent/0.0.1')

Next import whatever API you're interested in and pass it the
client you just created:

    .. code-block:: python

        from nextcloud_async.api import Conversations, Maps, GroupFolders

        conversations = Conversations(client)
        print(await conversations.list())

        maps = Maps(client)
        print(await maps.list_favorites())

        groupfolders = GroupFolders(client)
        print(await groupfolders.list())
