## Nextcloud Asynchronous Client
######

This project is not endorsed or recognized in any way by the NextCloud
project.

----

There is a `NextCloudAsync.get_conversations()` function already, and it works
perfectly fine, but that's too easy.

This is a perfectly horrible way to do it:



    import httpx
    import asyncio

    from nextcloud_async import NextCloudAsync

    nc = NextCloudAsync(
        client=httpx.AsyncClient(),
        user='user',
        password='password',
        endpoint='https://cloud.example.com')

    async def get_conversations():
        reqs = []
        conversations = await nc.get_conversations()
        for conv in conversations:
            reqs.append(nc.get_conversation(conv['token']))
        responses = await asyncio.gather(*reqs)

        print(responses)

    asyncio.run(get_conversations())

----

Tests are coming.
