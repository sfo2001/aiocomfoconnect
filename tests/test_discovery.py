"""Unit tests for Discovery functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from aiocomfoconnect.discovery import (
    discover_bridges,
    BridgeDiscoveryProtocol,
    DISCOVERY_REQUEST,
    DEFAULT_TIMEOUT,
    BROADCAST_FALLBACK
)
from aiocomfoconnect.bridge import Bridge
from aiocomfoconnect.protobuf import zehnder_pb2


class TestBridgeDiscoveryProtocol:
    """Test BridgeDiscoveryProtocol functionality."""
    
    def test_init_default(self):
        """Test BridgeDiscoveryProtocol initialization with defaults."""
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            
            assert protocol._bridges == []
            assert protocol._target is None
            assert protocol.transport is None
            mock_loop.return_value.call_later.assert_called_once_with(DEFAULT_TIMEOUT, protocol.disconnect)
    
    def test_init_with_target_and_timeout(self):
        """Test BridgeDiscoveryProtocol initialization with target and timeout."""
        target = "192.168.1.100"
        timeout = 5
        
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol(target=target, timeout=timeout)
            
            assert protocol._target == target
            mock_loop.return_value.call_later.assert_called_once_with(timeout, protocol.disconnect)
    
    def test_connection_made_with_target(self):
        """Test connection_made with specific target."""
        target = "192.168.1.100"
        mock_transport = MagicMock()
        
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol(target=target)
            protocol.connection_made(mock_transport)
            
            assert protocol.transport == mock_transport
            mock_transport.sendto.assert_called_once_with(DISCOVERY_REQUEST, (target, Bridge.PORT))
    
    def test_connection_made_broadcast(self):
        """Test connection_made with broadcast."""
        mock_transport = MagicMock()
        
        with patch('asyncio.get_running_loop') as mock_loop:
            with patch('netifaces.gateways') as mock_gateways:
                with patch('netifaces.ifaddresses') as mock_ifaddresses:
                    mock_loop.return_value.create_future.return_value = AsyncMock()
                    mock_loop.return_value.call_later.return_value = MagicMock()
                    
                    # Mock successful broadcast address detection
                    mock_gateways.return_value = {
                        'default': {2: ('192.168.1.1', 'eth0')}
                    }
                    mock_ifaddresses.return_value = {
                        2: [{'broadcast': '192.168.1.255'}]
                    }
                    
                    protocol = BridgeDiscoveryProtocol()
                    protocol.connection_made(mock_transport)
                    
                    assert protocol.transport == mock_transport
                    mock_transport.sendto.assert_called_once_with(DISCOVERY_REQUEST, ('192.168.1.255', Bridge.PORT))
    
    def test_connection_made_broadcast_fallback(self):
        """Test connection_made with broadcast fallback when detection fails."""
        mock_transport = MagicMock()
        
        with patch('asyncio.get_running_loop') as mock_loop:
            with patch('netifaces.gateways', side_effect=OSError("Network error")):
                mock_loop.return_value.create_future.return_value = AsyncMock()
                mock_loop.return_value.call_later.return_value = MagicMock()
                
                protocol = BridgeDiscoveryProtocol()
                protocol.connection_made(mock_transport)
                
                assert protocol.transport == mock_transport
                mock_transport.sendto.assert_called_once_with(DISCOVERY_REQUEST, (BROADCAST_FALLBACK, Bridge.PORT))
    
    def test_datagram_received_discovery_request(self):
        """Test receiving discovery request (should be ignored)."""
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            initial_bridges_count = len(protocol._bridges)
            
            protocol.datagram_received(DISCOVERY_REQUEST, ("192.168.1.100", 56747))
            
            assert len(protocol._bridges) == initial_bridges_count
    
    def test_datagram_received_valid_response(self):
        """Test receiving valid bridge response."""
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            
            # Create a mock protobuf response
            mock_response = zehnder_pb2.DiscoveryOperation()
            mock_response.searchGatewayResponse.ipaddress = "192.168.1.100"
            mock_response.searchGatewayResponse.uuid = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
            mock_response.searchGatewayResponse.version = 1  # Add required version field
            response_data = mock_response.SerializeToString()
            
            protocol.datagram_received(response_data, ("192.168.1.100", 56747))
            
            assert len(protocol._bridges) == 1
            bridge = protocol._bridges[0]
            assert bridge.host == "192.168.1.100"
            assert bridge.uuid == "000102030405060708090a0b0c0d0e0f"
    
    def test_datagram_received_invalid_response(self):
        """Test receiving invalid bridge response."""
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            
            # Send invalid data
            protocol.datagram_received(b"invalid_data", ("192.168.1.100", 56747))
            
            assert len(protocol._bridges) == 0
    
    def test_datagram_received_with_target_disconnects(self):
        """Test that receiving response with target disconnects immediately."""
        target = "192.168.1.100"
        mock_timeout = MagicMock()
        
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = AsyncMock()
            mock_loop.return_value.call_later.return_value = mock_timeout
            
            protocol = BridgeDiscoveryProtocol(target=target)
            
            # Create a mock protobuf response
            mock_response = zehnder_pb2.DiscoveryOperation()
            mock_response.searchGatewayResponse.ipaddress = target
            mock_response.searchGatewayResponse.uuid = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
            mock_response.searchGatewayResponse.version = 1  # Add required version field
            response_data = mock_response.SerializeToString()
            
            with patch.object(protocol, 'disconnect') as mock_disconnect:
                protocol.datagram_received(response_data, (target, 56747))
                
                mock_timeout.cancel.assert_called_once()
                mock_disconnect.assert_called_once()
    
    def test_disconnect(self):
        """Test disconnect functionality."""
        mock_transport = MagicMock()
        mock_future = MagicMock()
        mock_future.done.return_value = False
        
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = mock_future
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            protocol.transport = mock_transport
            protocol._bridges = [MagicMock()]
            
            protocol.disconnect()
            
            mock_transport.close.assert_called_once()
            mock_future.set_result.assert_called_once_with(protocol._bridges)
    
    def test_disconnect_no_transport(self):
        """Test disconnect when no transport exists."""
        mock_future = MagicMock()
        mock_future.done.return_value = False
        
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = mock_future
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            protocol.transport = None
            
            protocol.disconnect()
            
            mock_future.set_result.assert_called_once_with(protocol._bridges)
    
    def test_disconnect_future_already_done(self):
        """Test disconnect when future is already done."""
        mock_transport = MagicMock()
        mock_future = MagicMock()
        mock_future.done.return_value = True
        
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_loop.return_value.create_future.return_value = mock_future
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            protocol.transport = mock_transport
            
            protocol.disconnect()
            
            mock_transport.close.assert_called_once()
            mock_future.set_result.assert_not_called()
    
    def test_get_bridges(self):
        """Test get_bridges returns the future."""
        with patch('asyncio.get_running_loop') as mock_loop:
            mock_future = AsyncMock()
            mock_loop.return_value.create_future.return_value = mock_future
            mock_loop.return_value.call_later.return_value = MagicMock()
            
            protocol = BridgeDiscoveryProtocol()
            
            result = protocol.get_bridges()
            
            assert result == mock_future


class TestDiscoverBridges:
    """Test discover_bridges function."""
    
    @pytest.mark.asyncio
    async def test_discover_bridges_no_host(self):
        """Test discover_bridges without specific host."""
        mock_bridges = [Bridge("192.168.1.100", "test_uuid")]
        
        # Create a real future with the result we want
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        future.set_result(mock_bridges)
        
        with patch('aiocomfoconnect.discovery.BridgeDiscoveryProtocol') as mock_protocol_class:
            mock_protocol = MagicMock()
            mock_protocol.get_bridges.return_value = future
            mock_protocol_class.return_value = mock_protocol
            
            mock_transport = MagicMock()
            
            with patch.object(loop, 'create_datagram_endpoint') as mock_endpoint:
                mock_endpoint.return_value = (mock_transport, mock_protocol)
                
                result = await discover_bridges()
                
                assert result == mock_bridges
                mock_endpoint.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_bridges_with_host(self):
        """Test discover_bridges with specific host."""
        host = "192.168.1.100"
        mock_bridges = [Bridge(host, "test_uuid")]
        
        # Create a real future with the result we want
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        future.set_result(mock_bridges)
        
        with patch('aiocomfoconnect.discovery.BridgeDiscoveryProtocol') as mock_protocol_class:
            mock_protocol = MagicMock()
            mock_protocol.get_bridges.return_value = future
            mock_protocol_class.return_value = mock_protocol
            
            mock_transport = MagicMock()
            
            with patch.object(loop, 'create_datagram_endpoint') as mock_endpoint:
                mock_endpoint.return_value = (mock_transport, mock_protocol)
                
                result = await discover_bridges(host=host)
                
                assert result == mock_bridges
                mock_endpoint.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_bridges_with_timeout(self):
        """Test discover_bridges with custom timeout."""
        timeout = 5
        mock_bridges = []
        
        # Create a real future with the result we want
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        future.set_result(mock_bridges)
        
        with patch('aiocomfoconnect.discovery.BridgeDiscoveryProtocol') as mock_protocol_class:
            mock_protocol = MagicMock()
            mock_protocol.get_bridges.return_value = future
            mock_protocol_class.return_value = mock_protocol
            
            mock_transport = MagicMock()
            
            with patch.object(loop, 'create_datagram_endpoint') as mock_endpoint:
                mock_endpoint.return_value = (mock_transport, mock_protocol)
                
                result = await discover_bridges(timeout=timeout)
                
                assert result == mock_bridges
                mock_endpoint.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_bridges_with_custom_loop(self):
        """Test discover_bridges with custom event loop."""
        # Create a custom mock loop that behaves like a real event loop
        custom_loop = MagicMock()
        custom_loop.create_datagram_endpoint = AsyncMock()
        
        # Create a real future from the current running loop
        real_loop = asyncio.get_running_loop()
        future = real_loop.create_future()
        
        mock_bridges = []
        future.set_result(mock_bridges)
        
        with patch('aiocomfoconnect.discovery.BridgeDiscoveryProtocol') as mock_protocol_class:
            mock_protocol = MagicMock()
            mock_protocol.get_bridges.return_value = future
            mock_protocol_class.return_value = mock_protocol
            
            mock_transport = MagicMock()
            custom_loop.create_datagram_endpoint.return_value = (mock_transport, mock_protocol)
            
            result = await discover_bridges(loop=custom_loop)
            
            assert result == mock_bridges
            custom_loop.create_datagram_endpoint.assert_called_once()