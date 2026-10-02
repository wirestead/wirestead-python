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
    return hasattr(socket, "AF_UNIX")


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not supports_uds_loopback(),
    reason="Python does not expose AF_UNIX on this platform",
)
@pytest.mark.parametrize("method", ["send", "send_line"])
def test_uds_client_server_loopback(uds_socket_path, method):
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    socket_path = uds_socket_path

    received = []
    replies = []
    got_reply = threading.Event()
    connected = threading.Event()
    got_data = threading.Event()

    server = wirestead.UdsServer(socket_path)
    server.max_clients(1)
    server.on_connect(lambda ctx: connected.set())
    server.on_data(lambda ctx: (received.append(bytes(ctx.data)), got_data.set()))

    client = wirestead.UdsClient(socket_path)
    client.on_data(lambda ctx: (replies.append(bytes(ctx.data)), got_reply.set()))
    try:
        assert server.start_sync()
        assert client.start_sync()

        assert connected.wait(2.0)

        payload = "hello" if method == "send_line" else b"hello"
        assert getattr(client, method)(payload) is True
        assert got_data.wait(2.0)
        assert received == [b"hello\n" if method == "send_line" else b"hello"]
        assert server.send_to(server.connected_clients()[0], b"targeted") is True
        assert got_reply.wait(2.0)
        assert replies == [b"targeted"]
        got_reply.clear()
        assert server.broadcast(b"broadcast") is True
        assert got_reply.wait(2.0)
        assert replies == [b"targeted", b"broadcast"]
    finally:
        client.stop()
        server.stop()


@pytest.mark.skipif(
    not supports_uds_loopback(),
    reason="Python does not expose AF_UNIX on this platform",
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

    client = wirestead.UdsClient(socket_path)
    try:
        assert server.start_sync()
        assert client.start_sync()

        assert wait_until(lambda: client.connected())

        assert client.send(b'{"type":"metadata"}\n') is True
        assert got_message.wait(2.0)

        assert messages == ['{"type":"metadata"}']
    finally:
        client.stop()
        server.stop()
