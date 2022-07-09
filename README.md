## Nextcloud Asynchronous Client
######

This project is not endorsed or recognized in any way by the NextCloud
project.

----
### Example usage:

    > from nextcloud_async import NextCloudAsync
    > import httpx, asyncio

    > u = 'user'
    > p = 'password'
    > e = 'https://cloud.example.com'
    > c = httpx.AsyncClient()
    > nca = NextCloudAsync(client=c, user=u, password=p, endpoint=e)
    > users = asyncio.run(nca.get_users())
    > print(users)
    ['admin', 'slippinjimmy', 'chunks', 'flipper', 'squishface']
----