"""Pytest configuration and fixtures for aiocomfoconnect tests."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiocomfoconnect import Bridge, ComfoConnect
from aiocomfoconnect.protobuf import zehnder_pb2


@pytest.fixture
def mock_host():
    """Mock host IP address."""
    return "192.168.1.100"


@pytest.fixture
def mock_uuid():
    """Mock device UUID."""
    return "00000000000000000000000000000001"


@pytest.fixture
def mock_local_uuid():
    """Mock local application UUID."""
    return "00000000000000000000000000000002"


@pytest.fixture
def mock_pin():
    """Mock device PIN (4-digit as per Zehnder device constraint)."""
    return 1234


@pytest.fixture
def mock_stream_reader():
    """Mock asyncio StreamReader."""
    return AsyncMock(spec=asyncio.StreamReader)


@pytest.fixture
def mock_stream_writer():
    """Mock asyncio StreamWriter."""
    writer = AsyncMock(spec=asyncio.StreamWriter)
    writer.write = MagicMock()
    writer.drain = AsyncMock()
    writer.close = MagicMock()
    writer.wait_closed = AsyncMock()
    return writer


@pytest.fixture
def mock_bridge(mock_host, mock_uuid):
    """Mock Bridge instance."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return Bridge(mock_host, mock_uuid, loop=loop)


@pytest.fixture
def mock_comfoconnect(mock_host, mock_uuid):
    """Mock ComfoConnect instance."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return ComfoConnect(mock_host, mock_uuid, loop=loop)


@pytest.fixture
def mock_zehnder_message():
    """Mock zehnder protobuf message."""
    msg = zehnder_pb2.GatewayOperation()
    msg.type = zehnder_pb2.GatewayOperation.DISCOVERY_RESPONSE
    msg.reference = 1
    return msg


@pytest.fixture
def mock_open_connection():
    """Mock asyncio.open_connection."""
    with patch('asyncio.open_connection') as mock:
        yield mock


@pytest.fixture
def mock_create_datagram_endpoint():
    """Mock asyncio create_datagram_endpoint."""
    with patch('asyncio.get_event_loop') as mock_loop:
        mock_loop.return_value.create_datagram_endpoint = AsyncMock()
        yield mock_loop.return_value.create_datagram_endpoint


