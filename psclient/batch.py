import asyncio

from .psclient import AIOPSClient


async def async_execute(statements, client_class=AIOPSClient, **kwargs):
    """

    :param statements:
    :param client_class:
    :param kwargs:
    :return:
    """
    async def _run(client, stm):
        """

        :param client:
        :param stm:
        :return:
        """
        await client.connect()
        resp = await client.execute(stm)
        await client.disconnect()
        return resp

    tasks = []
    for s in statements:
        tasks.append(_run(client_class(**kwargs), s))

    return await asyncio.gather(*tasks, return_exceptions=True)


def batch(statements, **kwargs):
    """

    :param statements:
    :return:
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_execute(statements, **kwargs))
