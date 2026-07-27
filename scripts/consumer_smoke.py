#!/usr/bin/env python3
"""Validate an installed Wirestead wheel from outside the source tree."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
from pathlib import Path
import socket
import sys
import threading
import time
import traceback


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _wait_until(predicate, timeout: float = 5.0, interval: float = 0.01) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def _reserve_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _reserve_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _assert_imported_from_wheel(wirestead, project_root: Path) -> None:
    module_file = Path(wirestead.__file__).resolve()
    source_package = (project_root / "src" / "wirestead").resolve()
    if _is_relative_to(module_file, source_package):
        raise AssertionError(f"imported from source tree instead of installed wheel: {module_file}")
    print(f"wirestead module: {module_file}", flush=True)


def _tcp_loopback(wirestead) -> None:
    port = _reserve_tcp_port()
    connected = threading.Event()
    got_message = threading.Event()
    received: list[bytes] = []

    server = wirestead.TcpServer(port)
    client = wirestead.TcpClient("127.0.0.1", port)

    try:
        server.use_line_framer("\n")
        server.on_connect(lambda _ctx: connected.set())
        server.on_message(lambda ctx: (received.append(bytes(ctx.data)), got_message.set()))

        assert server.start() is True
        assert _wait_until(server.listening), "TCP server did not start listening"

        assert client.start() is True
        assert _wait_until(lambda: connected.is_set() and client.connected()), "TCP client did not connect"

        assert client.send_line("wheel-tcp")
        assert got_message.wait(5.0), "TCP loopback did not receive data"
        assert received == [b"wheel-tcp"]
    finally:
        client.stop()
        server.stop()


def _udp_loopback(wirestead) -> None:
    port = _reserve_udp_port()
    got_data = threading.Event()
    received: list[bytes] = []

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
        assert _wait_until(server.listening), "UDP server did not start listening"

        assert client.start_sync() is True
        assert _wait_until(client.connected), "UDP client did not report connected"

        assert client.send(b"wheel-udp")
        assert got_data.wait(5.0), "UDP loopback did not receive data"
        assert received == [b"wheel-udp"]
    finally:
        client.stop()
        server.stop()


def _run_smoke(expected_version: str | None, project_root: Path) -> None:
    import wirestead

    print(f"python: {sys.executable}", flush=True)
    print(f"cwd: {Path.cwd()}", flush=True)
    _assert_imported_from_wheel(wirestead, project_root)

    version = getattr(wirestead, "__version__", None)
    print(f"wirestead version: {version}", flush=True)
    if expected_version and version != expected_version:
        raise AssertionError(f"expected version {expected_version}, got {version}")

    _tcp_loopback(wirestead)
    print("TCP loopback: ok", flush=True)
    _udp_loopback(wirestead)
    print("UDP loopback: ok", flush=True)


def _child(expected_version: str | None, project_root: str, queue) -> None:
    try:
        _run_smoke(expected_version, Path(project_root).resolve())
    except BaseException:
        queue.put((False, traceback.format_exc()))
    else:
        queue.put((True, ""))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-version")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(
        target=_child,
        args=(args.expected_version, str(Path(args.project_root).resolve()), queue),
    )
    process.start()
    process.join(args.timeout)

    if process.is_alive():
        process.terminate()
        process.join(5.0)
        print(f"consumer smoke timed out after {args.timeout:.0f}s", file=sys.stderr)
        return 124

    if queue.empty():
        print(f"consumer smoke exited without a result, code={process.exitcode}", file=sys.stderr)
        return process.exitcode or 1

    ok, details = queue.get()
    if not ok:
        print(details, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
