#!/usr/bin/env python3
"""Isolate Windows TcpServer crashes without hiding pytest failures."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import textwrap


def _reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _run_case(name: str, source: str) -> int:
    workdir = Path(tempfile.mkdtemp(prefix="wirestead-tcp-diagnose-"))
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    print(f"::group::{name}", flush=True)
    print(f"cwd={workdir}", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-X", "faulthandler", "-c", textwrap.dedent(source)],
            cwd=workdir,
            env=env,
            text=True,
            timeout=15.0,
        )
    except subprocess.TimeoutExpired:
        print("timed out after 15s", flush=True)
        print("::endgroup::", flush=True)
        return 124
    print(f"exitcode={result.returncode}", flush=True)
    print("::endgroup::", flush=True)
    return result.returncode


def main() -> int:
    port = _reserve_port()
    loopback_port = _reserve_port()
    cases = {
        "construct": """
            import wirestead
            print(wirestead.__file__, flush=True)
            server = wirestead.TcpServer(0)
            print("constructed", flush=True)
            server.stop()
            print("stopped", flush=True)
        """,
        "start_port_zero": """
            import wirestead
            server = wirestead.TcpServer(0)
            print("before start", flush=True)
            print(server.start(), flush=True)
            print("listening", server.listening(), flush=True)
            server.stop()
            print("stopped", flush=True)
        """,
        "start_reserved_any": f"""
            import wirestead
            server = wirestead.TcpServer({port})
            print("before start", flush=True)
            print(server.start(), flush=True)
            print("listening", server.listening(), flush=True)
            server.stop()
            print("stopped", flush=True)
        """,
        "start_reserved_loopback": f"""
            import wirestead
            server = wirestead.TcpServer({port})
            server.bind_address("127.0.0.1")
            print("before start", flush=True)
            print(server.start(), flush=True)
            print("listening", server.listening(), flush=True)
            server.stop()
            print("stopped", flush=True)
        """,
        "server_loopback": f"""
            import socket
            import time
            import wirestead

            def wait_until(predicate, timeout=5.0, interval=0.01):
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    if predicate():
                        return True
                    time.sleep(interval)
                return False

            server = wirestead.TcpServer({loopback_port})
            try:
                print("before bind", flush=True)
                server.bind_address("127.0.0.1")
                print("before start", flush=True)
                print("start", server.start(), flush=True)
                print("listening", server.listening(), flush=True)
                print("before connect", flush=True)
                peer = socket.create_connection(("127.0.0.1", {loopback_port}), timeout=3.0)
                with peer:
                    peer.settimeout(3.0)
                    print("connected", flush=True)
                    print("before client_count", flush=True)
                    print("client_count_ready", wait_until(lambda: server.client_count() == 1), flush=True)
                    print("client_count", server.client_count(), flush=True)
                    print("before broadcast", flush=True)
                    print("broadcast", server.broadcast(b"diag-tcp\\n"), flush=True)
                    print("before recv", flush=True)
                    print("recv", peer.recv(1024), flush=True)
                    print("peer closed", flush=True)
            finally:
                print("before stop", flush=True)
                server.stop()
                print("stopped", flush=True)
        """,
    }

    failed = False
    for name, source in cases.items():
        failed = _run_case(name, source) != 0 or failed

    if failed:
        print("One or more TcpServer diagnostic cases failed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
