"""Regression tests: blocking send paths must release the GIL.

The default backpressure strategy is ``Reliable``, so ``send``/``send_line``/
``send_to``/``broadcast`` block the calling thread until send-queue pressure is
relieved. A binding that holds the GIL across that wait freezes every other
Python thread, including the ones a caller would use to drain the queue or to
call ``stop()``, so the interpreter cannot recover on its own.

Each scenario runs in a subprocess: when the GIL is starved no in-process
watchdog can fire, so a regression would hang the test session instead of
failing it. The subprocess timeout turns that hang into a normal failure.
"""

import os
import socket
import subprocess
import sys

import pytest

RUN_LOOPBACK_TESTS = os.environ.get("WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS") == "1"

pytestmark = pytest.mark.integration

# Seconds the parent allows the child to finish. Generous relative to the ~1s
# the child spends measuring, so only a real stall trips it.
_SCENARIO_TIMEOUT = 60.0

# Ticks the parent requires the child's timer thread to record while a blocking
# send is in flight. The child ticks every 10ms for ~1s; requiring 10 leaves a
# wide margin for slow/loaded CI while still being far above the 0-2 ticks a
# GIL-starved run produces.
_MIN_TICKS = 10

_SCENARIO = r'''
import os, socket, sys, tempfile, threading, time
import wirestead

kind = sys.argv[1]
BLOB = b"x" * 200_000
THRESHOLD = 1024

# The peer must stop draining almost immediately, otherwise the transport keeps
# flushing the send queue and the send never blocks long enough to be
# measurable. A small receive buffer saturates within the first few sends.
PEER_RCVBUF = 2048


# Sockets and transports must outlive the setup helpers. If they are collected
# the peer disconnects, sends fail fast instead of blocking, and the scenario
# silently stops testing anything.
_KEEPALIVE = []


def throttle(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, PEER_RCVBUF)
    _KEEPALIVE.append(sock)
    return sock


def stalled_client_transport():
    """A wirestead client whose peer accepts but never reads."""
    if kind == "uds_client":
        path = os.path.join(tempfile.mkdtemp(), "u.sock")
        listener = throttle(socket.socket(socket.AF_UNIX, socket.SOCK_STREAM))
        listener.bind(path)
        listener.listen(1)
        client = wirestead.UdsClient(path)
    else:
        listener = throttle(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        client = wirestead.TcpClient("127.0.0.1", listener.getsockname()[1])

    client.backpressure_threshold = THRESHOLD
    assert client.start(), "client failed to connect"
    _KEEPALIVE.append(listener.accept()[0])  # accepted, never read -> queue fills
    return lambda: client.send_line(BLOB)


def stalled_server_transport():
    """A wirestead server whose only client never reads."""
    if kind == "uds_server":
        path = os.path.join(tempfile.mkdtemp(), "u.sock")
        server = wirestead.UdsServer(path)
        server.backpressure_threshold = THRESHOLD
        assert server.start_sync(), "server failed to listen"
        peer = throttle(socket.socket(socket.AF_UNIX, socket.SOCK_STREAM))
        peer.connect(path)
    else:
        # TcpServer does not expose the bound port, so reserve an ephemeral one
        # and hand the number over.
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()

        server = wirestead.TcpServer(port)
        server.backpressure_threshold = THRESHOLD
        assert server.start_sync(), "server failed to listen"
        peer = throttle(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        peer.connect(("127.0.0.1", port))

    deadline = time.time() + 5.0
    while server.client_count() == 0 and time.time() < deadline:
        time.sleep(0.01)
    assert server.client_count() == 1, "client did not register on the server"

    if kind.endswith("broadcast"):
        return lambda: server.broadcast(BLOB)
    client_id = server.connected_clients()[0]
    return lambda: server.send_to(client_id, BLOB)


send_once = (
    stalled_client_transport()
    if kind.endswith("_client")
    else stalled_server_transport()
)

ticks = [0]


def ticker():
    while True:
        ticks[0] += 1
        time.sleep(0.01)


def sender():
    # Blocks once the queue passes the threshold. Holds the GIL if the
    # binding forgot to release it.
    while True:
        send_once()


threading.Thread(target=ticker, daemon=True).start()
threading.Thread(target=sender, daemon=True).start()

time.sleep(0.05)
before = ticks[0]
deadline = time.time() + 1.0
while time.time() < deadline:
    time.sleep(0.05)

print(ticks[0] - before, flush=True)

# The sender thread is parked inside a blocking send; a normal interpreter
# shutdown would join it. Leave immediately instead.
os._exit(0)
'''


def _tick_count(kind):
    """Run a scenario and return how many ticks the timer thread recorded."""
    try:
        proc = subprocess.run(
            [sys.executable, "-u", "-c", _SCENARIO, kind],
            capture_output=True,
            text=True,
            timeout=_SCENARIO_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"[{kind}] interpreter never made progress within {_SCENARIO_TIMEOUT}s: "
            "the blocking send held the GIL and starved every other Python thread"
        )

    assert proc.returncode == 0, (
        f"[{kind}] scenario failed (rc={proc.returncode})\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    return int(proc.stdout.strip().splitlines()[-1])


def _requires_loopback():
    if not RUN_LOOPBACK_TESTS:
        pytest.skip(
            "set WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 to enable real transport loopback tests"
        )


def _supports_uds():
    return os.name != "nt" and hasattr(socket, "AF_UNIX")


@pytest.mark.parametrize(
    "kind",
    [
        "tcp_client",
        "tcp_server",
        "tcp_server_broadcast",
        pytest.param(
            "uds_client",
            marks=pytest.mark.skipif(
                not _supports_uds(),
                reason="UDS loopback is validated on Linux/macOS; Windows validation is pending",
            ),
        ),
        pytest.param(
            "uds_server",
            marks=pytest.mark.skipif(
                not _supports_uds(),
                reason="UDS loopback is validated on Linux/macOS; Windows validation is pending",
            ),
        ),
    ],
)
def test_blocking_send_releases_gil(kind):
    _requires_loopback()

    ticks = _tick_count(kind)

    assert ticks >= _MIN_TICKS, (
        f"[{kind}] a background thread recorded only {ticks} ticks (expected >= {_MIN_TICKS}) "
        "while a blocking send was in flight; the binding is not releasing the GIL"
    )
