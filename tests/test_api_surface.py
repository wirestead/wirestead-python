def test_core_api_surface():
    import wirestead

    expected = [
        "TcpClient",
        "TcpServer",
        "Serial",
        "UdpClient",
        "UdpConfig",
        "UdpServer",
        "UdsClient",
        "UdsServer",
        "MessageContext",
        "ConnectionContext",
        "ErrorContext",
        "BackpressureStrategy",
        "ErrorCode",
        "LineFramer",
        "PacketFramer",
    ]

    missing = [name for name in expected if not hasattr(wirestead, name)]
    assert not missing


def test_standard_python_surface_uses_canonical_names():
    import wirestead

    assert hasattr(wirestead.TcpClient, "connected")
    assert not hasattr(wirestead.TcpClient, "is_connected")
    assert hasattr(wirestead.TcpClient, "use_line_framer")
    assert not hasattr(wirestead.TcpClient, "line_framer")
    assert hasattr(wirestead.TcpClient, "use_packet_framer")
    assert not hasattr(wirestead.TcpClient, "packet_framer")

    assert hasattr(wirestead.TcpServer, "listening")
    assert not hasattr(wirestead.TcpServer, "is_listening")
    assert hasattr(wirestead.TcpServer, "on_connect")
    assert not hasattr(wirestead.TcpServer, "on_client_connect")
    assert hasattr(wirestead.TcpServer, "on_disconnect")
    assert not hasattr(wirestead.TcpServer, "on_client_disconnect")

    assert hasattr(wirestead.MessageContext, "client_info")
    assert not hasattr(wirestead.MessageContext, "remote_address")


def test_backpressure_properties_are_write_only():
    import pytest
    import wirestead

    client = wirestead.TcpClient("127.0.0.1", 65535)

    client.backpressure_threshold = 32
    client.backpressure_strategy = wirestead.BackpressureStrategy.BestEffort

    with pytest.raises(AttributeError):
        _ = client.backpressure_threshold
    with pytest.raises(AttributeError):
        _ = client.backpressure_strategy


def test_uds_api_surface():
    import wirestead

    assert hasattr(wirestead, "UdsClient")
    assert hasattr(wirestead, "UdsServer")


def test_async_uds_api_surface():
    from wirestead.asyncio import AsyncUdsClient, AsyncUdsServer

    assert AsyncUdsClient is not None
    assert AsyncUdsServer is not None
