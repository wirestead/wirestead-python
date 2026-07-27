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
    }

    failed = False
    for name, source in cases.items():
        failed = _run_case(name, source) != 0 or failed

    if failed:
        print("One or more TcpServer diagnostic cases failed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
