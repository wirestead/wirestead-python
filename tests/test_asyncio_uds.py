import asyncio
import os
import socket

import pytest
import wirestead
from wirestead.asyncio import AsyncUdsClient

RUN_LOOPBACK_TESTS = os.environ.get("WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS") == "1"


def supports_uds_loopback():
    return hasattr(socket, "AF_UNIX")


async def wait_until(predicate, timeout=2.0, interval=0.01):
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        if predicate():
            return True
        await asyncio.sleep(interval)
    return False


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.skipif(
    not supports_uds_loopback(),
    reason="Python does not expose AF_UNIX on this platform",
)
async def test_async_uds_client_reads_line_message(uds_socket_path):
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    socket_path = uds_socket_path

    server = wirestead.UdsServer(socket_path)
    server.use_line_framer("\n", False, 65536)
    assert server.start_sync()

    client = AsyncUdsClient(socket_path)
    client.use_line_framer("\n", False, 65536)
    try:
        assert await client.start()
        assert await wait_until(lambda: server.client_count() > 0)

        assert server.broadcast(b'{"seq":1}\n')

        ctx = await asyncio.wait_for(client.read_message(), timeout=2.0)
        assert bytes(ctx.data).decode("utf-8") == '{"seq":1}'
    finally:
        client.stop()
        server.stop()
