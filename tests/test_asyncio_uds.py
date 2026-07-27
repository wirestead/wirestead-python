import asyncio
import os
import socket

import pytest
import wirestead
from wirestead.asyncio import AsyncUdsClient

RUN_LOOPBACK_TESTS = os.environ.get("WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS") == "1"


def supports_uds_loopback():
    return os.name != "nt" and hasattr(socket, "AF_UNIX")


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.skipif(
    not supports_uds_loopback(),
    reason="UDS loopback is validated on Linux/macOS; Windows validation is pending",
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
    assert await client.start()

    assert server.broadcast(b'{"seq":1}\n')

    ctx = await asyncio.wait_for(client.read_message(), timeout=2.0)
    assert bytes(ctx.data).decode("utf-8") == '{"seq":1}'

    client.stop()
    server.stop()
