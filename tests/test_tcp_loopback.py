import os
import socket
import threading
import time

import pytest

RUN_LOOPBACK_TESTS = os.environ.get("WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS") == "1"


def wait_until(predicate, timeout=5.0, interval=0.01):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def reserve_tcp_port():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]
    except PermissionError as exc:
        pytest.skip(f"socket creation is blocked in this environment: {exc}")


@pytest.mark.integration
def test_tcp_loopback_smoke():
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    import wirestead

    port = reserve_tcp_port()
    server_connected = threading.Event()
    server_message = threading.Event()
    received = []

    server = wirestead.TcpServer(port)
    client = wirestead.TcpClient("127.0.0.1", port)

    def on_connect(_ctx):
        server_connected.set()

    def on_message(ctx):
        received.append(ctx.data)
        server_message.set()

    try:
        server.use_line_framer("\n")
        server.bind_address("127.0.0.1")
        server.on_connect(on_connect)
        server.on_message(on_message)

        assert server.start() is True
        assert wait_until(server.listening)

        assert client.start() is True
        assert wait_until(lambda: server_connected.is_set() and client.connected())

        assert client.send_line("hello")
        assert wait_until(server_message.is_set)
        assert received == [b"hello"]
    finally:
        client.stop()
        server.stop()
