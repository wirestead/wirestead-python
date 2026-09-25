"""The Python bool contract must survive the C++ structured-result migration."""

import pytest


CLIENT_METHODS = [
    ("TcpClient", "send"),
    ("TcpClient", "send_line"),
    ("TcpClient", "send_blocking"),
    ("UdpClient", "send"),
    ("UdpClient", "send_line"),
    ("UdsClient", "send"),
    ("UdsClient", "send_line"),
    ("Serial", "send"),
    ("Serial", "send_line"),
]


def make_transport(name, path):
    import wirestead

    factories = {
        "TcpClient": lambda: wirestead.TcpClient("127.0.0.1", 65535),
        "TcpServer": lambda: wirestead.TcpServer(0),
        "UdpClient": lambda: wirestead.UdpClient(wirestead.UdpConfig()),
        "UdpServer": lambda: wirestead.UdpServer(0),
        "UdsClient": lambda: wirestead.UdsClient(path),
        "UdsServer": lambda: wirestead.UdsServer(path),
        # No device is opened: this test deliberately never starts the wrapper.
        "Serial": lambda: wirestead.Serial(path, 9600),
    }
    return factories[name]()


@pytest.mark.parametrize(("transport", "method"), CLIENT_METHODS)
def test_unstarted_client_send_is_python_false(transport, method, uds_socket_path):
    client = make_transport(transport, uds_socket_path)
    payload = "payload" if method == "send_line" else b"payload"
    assert getattr(client, method)(payload) is False


@pytest.mark.parametrize("transport", ["TcpServer", "UdpServer", "UdsServer"])
@pytest.mark.parametrize("method", ["send_to", "broadcast"])
def test_unstarted_server_send_is_python_false(transport, method, uds_socket_path):
    server = make_transport(transport, uds_socket_path)
    if method == "send_to":
        assert server.send_to(1, b"payload") is False
    else:
        # Zero targets must convert to False, not an unregistered C++ object.
        assert server.broadcast(b"payload") is False
