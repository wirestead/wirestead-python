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
def test_tcp_server_loopback_smoke():
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    import wirestead

    port = reserve_tcp_port()
    server = wirestead.TcpServer(port)

    try:
        server.bind_address("127.0.0.1")
        assert server.start() is True
        assert wait_until(server.listening)

        with socket.create_connection(("127.0.0.1", port), timeout=3.0) as peer:
            peer.settimeout(3.0)
            assert wait_until(lambda: server.client_count() == 1)
            assert server.broadcast(b"hello\n")
            assert peer.recv(1024) == b"hello\n"
    finally:
        server.stop()


@pytest.mark.integration
def test_tcp_server_runtime_stats_track_traffic():
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    import wirestead

    port = reserve_tcp_port()
    server = wirestead.TcpServer(port)
    payload = b"stats-probe\n"

    try:
        server.bind_address("127.0.0.1")
        assert server.start() is True
        assert wait_until(server.listening)

        with socket.create_connection(("127.0.0.1", port), timeout=3.0) as peer:
            peer.settimeout(3.0)
            assert wait_until(lambda: server.client_count() == 1)

            assert server.stats().bytes_accepted == 0

            assert server.broadcast(payload)
            assert peer.recv(1024) == payload
            peer.sendall(payload)
            assert wait_until(lambda: server.stats().bytes_received >= len(payload))

            stats = server.stats()
            assert stats.bytes_accepted >= len(payload)
            assert stats.messages_accepted >= 1
            assert stats.bytes_received >= len(payload)
            assert stats.dropped_bytes == 0
            assert stats.failed_sends == 0

            # The counters are a snapshot, so an earlier one keeps its values.
            server.reset_stats()
            assert server.stats().bytes_accepted == 0
            assert stats.bytes_accepted >= len(payload)
    finally:
        server.stop()


@pytest.mark.integration
def test_tcp_client_loopback_smoke():
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )

    import wirestead

    port = reserve_tcp_port()
    ready = threading.Event()
    received = []
    errors = []

    def socket_server():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind(("127.0.0.1", port))
                server_sock.listen(1)
                server_sock.settimeout(5.0)
                ready.set()
                conn, _addr = server_sock.accept()
                with conn:
                    conn.settimeout(5.0)
                    received.append(conn.recv(1024))
        except Exception as exc:  # pragma: no cover - surfaced by assertions below
            errors.append(exc)
            ready.set()

    thread = threading.Thread(target=socket_server, daemon=True)
    thread.start()
    assert ready.wait(5.0)

    client = wirestead.TcpClient("127.0.0.1", port)

    try:
        assert client.start() is True
        assert wait_until(client.connected)
        assert client.send_line("hello")
        assert wait_until(lambda: bool(received) or bool(errors))
        assert not errors
        assert received == [b"hello\n"]
    finally:
        client.stop()
        thread.join(timeout=5.0)
