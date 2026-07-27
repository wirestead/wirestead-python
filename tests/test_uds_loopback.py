import os
import socket
import threading
import time

import pytest
import wirestead

RUN_LOOPBACK_TESTS = os.environ.get("WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS") == "1"


def wait_until(predicate, timeout=5.0, interval=0.01):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def supports_uds_loopback():
    return os.name != "nt" and hasattr(socket, "AF_UNIX")


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not supports_uds_loopback(),
    reason="UDS loopback is validated on Linux/macOS; Windows validation is pending",
)
def test_uds_client_server_loopback(uds_socket_path):
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    socket_path = uds_socket_path

    received = []
    connected = threading.Event()
    got_data = threading.Event()

    server = wirestead.UdsServer(socket_path)
    server.max_clients(1)
    server.on_connect(lambda ctx: connected.set())
    server.on_data(lambda ctx: (received.append(bytes(ctx.data)), got_data.set()))

    assert server.start_sync()

    client = wirestead.UdsClient(socket_path)
    assert client.start_sync()

    assert connected.wait(2.0)

    assert client.send(b"hello")
    assert got_data.wait(2.0)
    assert received == [b"hello"]

    client.stop()
    server.stop()


@pytest.mark.skipif(
    not supports_uds_loopback(),
    reason="UDS loopback is validated on Linux/macOS; Windows validation is pending",
)
def test_uds_line_framer_jsonl(uds_socket_path):
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    socket_path = uds_socket_path

    messages = []
    got_message = threading.Event()

    server = wirestead.UdsServer(socket_path)
    server.use_line_framer("\n", False, 65536)
    server.on_message(
        lambda ctx: (messages.append(bytes(ctx.data).decode("utf-8")), got_message.set())
    )

    assert server.start_sync()

    client = wirestead.UdsClient(socket_path)
    assert client.start_sync()

    # Wait for connection
    assert wait_until(lambda: client.connected())

    assert client.send(b'{"type":"metadata"}\n')
    assert got_message.wait(2.0)

    assert messages == ['{"type":"metadata"}']

    client.stop()
    server.stop()
