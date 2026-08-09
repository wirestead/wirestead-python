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
        "RuntimeStats",
    ]

    missing = [name for name in expected if not hasattr(wirestead, name)]
    assert not missing


RUNTIME_STATS_FIELDS = (
    "bytes_accepted",
    "messages_accepted",
    "bytes_sent",
    "messages_sent",
    "bytes_received",
    "messages_received",
    "failed_sends",
    "dropped_messages",
    "dropped_bytes",
    "backpressure_events",
    "queued_bytes",
    "pending_bytes",
    "max_queued_bytes",
    "backpressure_active",
)


def test_every_transport_exposes_stats():
    import wirestead

    transports = (
        wirestead.TcpClient,
        wirestead.TcpServer,
        wirestead.Serial,
        wirestead.UdsClient,
        wirestead.UdsServer,
        wirestead.UdpClient,
        wirestead.UdpServer,
    )

    missing = [
        f"{cls.__name__}.{name}"
        for cls in transports
        for name in ("stats", "reset_stats")
        if not hasattr(cls, name)
    ]
    assert not missing


def test_runtime_stats_snapshot_has_every_counter():
    import wirestead

    # Constructing does not connect, so nothing has moved yet.
    stats = wirestead.TcpClient("127.0.0.1", 65535).stats()

    assert isinstance(stats, wirestead.RuntimeStats)

    missing = [name for name in RUNTIME_STATS_FIELDS if not hasattr(stats, name)]
    assert not missing

    assert stats.bytes_accepted == 0
    assert stats.bytes_sent == 0
    assert stats.bytes_received == 0
    assert stats.dropped_bytes == 0
    assert stats.backpressure_events == 0
    assert stats.backpressure_active is False

    assert "RuntimeStats" in repr(stats)


def test_runtime_stats_fields_are_read_only():
    import pytest
    import wirestead

    stats = wirestead.TcpClient("127.0.0.1", 65535).stats()

    with pytest.raises(AttributeError):
        stats.bytes_sent = 123
    with pytest.raises(AttributeError):
        stats.backpressure_active = True


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
