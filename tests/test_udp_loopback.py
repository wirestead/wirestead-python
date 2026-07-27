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


def reserve_udp_port():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]
    except PermissionError as exc:
        pytest.skip(f"socket creation is blocked in this environment: {exc}")


@pytest.mark.integration
def test_udp_loopback_smoke():
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    import wirestead

    port = reserve_udp_port()
    got_data = threading.Event()
    received = []

    server_cfg = wirestead.UdpConfig()
    server_cfg.bind_address = "127.0.0.1"
    server_cfg.local_port = port

    client_cfg = wirestead.UdpConfig()
    client_cfg.bind_address = "127.0.0.1"
    client_cfg.local_port = 0
    client_cfg.remote_address = "127.0.0.1"
    client_cfg.remote_port = port

    server = wirestead.UdpServer(server_cfg)
    client = wirestead.UdpClient(client_cfg)

    try:
        server.on_data(lambda ctx: (received.append(bytes(ctx.data)), got_data.set()))

        assert server.start_sync() is True
        assert wait_until(server.listening)

        assert client.start_sync() is True
        assert wait_until(client.connected)

        assert client.send(b"hello udp")
        assert got_data.wait(5.0)
        assert received == [b"hello udp"]
    finally:
        client.stop()
        server.stop()
