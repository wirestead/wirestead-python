import os
import tempfile
import pytest


@pytest.fixture
def uds_socket_path():
    # Keep the path below sockaddr_un limits on macOS and Windows.
    with tempfile.TemporaryDirectory(dir=_short_tmpdir()) as d:
        yield os.path.join(d, "u.sock")


def _short_tmpdir():
    # On macOS, gettempdir() returns a long per-user path under /var/folders.
    # /tmp is a symlink to /private/tmp and is always short enough.
    candidates = [tempfile.gettempdir()] if os.name == "nt" else ["/tmp", tempfile.gettempdir()]
    for c in candidates:
        if os.path.isdir(c) and len(c) < 60:
            return c
    return tempfile.gettempdir()
