"""Unit tests for Bridge class."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from aiocomfoconnect.bridge import Bridge, EventBus, Message, SelfDeregistrationError
from aiocomfoconnect.exceptions import (
    AioComfoConnectNotConnected,
    AioComfoConnectTimeout,
    ComfoConnectNotAllowed,
)
from aiocomfoconnect.protobuf import zehnder_pb2


class TestEventBus:
    """Test EventBus functionality."""
    
    def test_init(self):
        """Test EventBus initialization."""
        event_bus = EventBus()
        assert event_bus.listeners == {}
    
    def test_add_listener(self):
        """Test adding a listener to the event bus."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_bus = EventBus()
        future = loop.create_future()
        
        event_bus.add_listener(1, future)
        
        assert 1 in event_bus.listeners
        assert future in event_bus.listeners[1]
        loop.close()
    
    def test_add_multiple_listeners_same_event(self):
        """Test adding multiple listeners to the same event."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_bus = EventBus()
        future1 = loop.create_future()
        future2 = loop.create_future()
        
        event_bus.add_listener(1, future1)
        event_bus.add_listener(1, future2)
        
        assert len(event_bus.listeners[1]) == 2
        loop.close()
    
    def test_emit_success(self):
        """Test emitting a successful event."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_bus = EventBus()
        future = loop.create_future()
        test_result = "test_result"
        
        event_bus.add_listener(1, future)
        event_bus.emit(1, test_result)
        
        assert future.result() == test_result
        assert 1 not in event_bus.listeners
        loop.close()
    
    def test_emit_exception(self):
        """Test emitting an exception event."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        event_bus = EventBus()
        future = loop.create_future()
        test_exception = ValueError("test error")
        
        event_bus.add_listener(1, future)
        event_bus.emit(1, test_exception)
        
        assert future.exception() == test_exception
        assert 1 not in event_bus.listeners
        loop.close()
    
    def test_emit_no_listeners(self):
        """Test emitting event with no listeners."""
        event_bus = EventBus()
        event_bus.emit(1, "test")
        assert 1 not in event_bus.listeners


class TestBridge:
    """Test Bridge functionality."""
    
    def test_init(self, mock_host, mock_uuid):
        """Test Bridge initialization."""
        loop = asyncio.new_event_loop()
        bridge = Bridge(mock_host, mock_uuid, loop=loop)
        
        assert bridge.host == mock_host
        assert bridge.uuid == mock_uuid
        assert bridge._local_uuid is None
        assert bridge._reader is None
        assert bridge._writer is None
        assert bridge._reference is None
        assert bridge._event_bus is None
        assert bridge.PORT == 56747
        loop.close()
    
    def test_repr(self, mock_host, mock_uuid):
        """Test Bridge string representation."""
        loop = asyncio.new_event_loop()
        bridge = Bridge(mock_host, mock_uuid, loop=loop)
        expected = f"<Bridge {mock_host}, UID={mock_uuid}>"
        assert repr(bridge) == expected
        loop.close()
    
    def test_set_sensor_callback(self, mock_bridge):
        """Test setting sensor callback."""
        callback = MagicMock()
        mock_bridge.set_sensor_callback(callback)
        assert mock_bridge._Bridge__sensor_callback_fn == callback
    
    def test_set_alarm_callback(self, mock_bridge):
        """Test setting alarm callback."""
        callback = MagicMock()
        mock_bridge.set_alarm_callback(callback)
        assert mock_bridge._Bridge__alarm_callback_fn == callback
    
    @pytest.mark.asyncio
    async def test_connect_success(self, mock_bridge, mock_local_uuid, mock_open_connection):
        """Test successful connection."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        
        # Mock the loop.create_task to avoid event loop issues
        with patch.object(mock_bridge._loop, 'create_task') as mock_create_task:
            mock_task = AsyncMock()
            mock_create_task.return_value = mock_task
            
            result_task = await mock_bridge._connect(mock_local_uuid)
        
        mock_open_connection.assert_called_once_with(mock_bridge.host, mock_bridge.PORT)
        assert mock_bridge._local_uuid == mock_local_uuid
        assert mock_bridge._reader == mock_reader
        assert mock_bridge._writer == mock_writer
        assert mock_bridge._reference == 1
        assert isinstance(mock_bridge._event_bus, EventBus)
        assert result_task == mock_task
        mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_bridge, mock_local_uuid, mock_open_connection):
        """Test connection failure."""
        mock_open_connection.side_effect = ConnectionRefusedError("Connection refused")
        
        with pytest.raises(ConnectionRefusedError):
            await mock_bridge._connect(mock_local_uuid)
    
    @pytest.mark.asyncio
    async def test_disconnect_success(self, mock_bridge):
        """Test successful disconnection."""
        mock_writer = MagicMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()
        
        # Create a proper task-like mock
        async def mock_task_coro():
            pass
        
        mock_read_task = asyncio.create_task(mock_task_coro())
        mock_bridge._writer = mock_writer
        mock_bridge._read_task = mock_read_task
        
        await mock_bridge._disconnect()
        
        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_called_once()
        assert mock_bridge._read_task is None
    
    @pytest.mark.asyncio
    async def test_disconnect_no_connection(self, mock_bridge):
        """Test disconnection when not connected."""
        await mock_bridge._disconnect()
        assert mock_bridge._read_task is None
    
    def test_is_connected_true(self, mock_bridge):
        """Test is_connected when connected."""
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = False
        mock_bridge._writer = mock_writer
        assert mock_bridge.is_connected() is True
    
    def test_is_connected_false(self, mock_bridge):
        """Test is_connected when not connected."""
        assert mock_bridge.is_connected() is False
    
    @pytest.mark.asyncio
    async def test_cmd_register_app(self, mock_bridge, mock_local_uuid, mock_pin):
        """Test app registration command."""
        device_name = "test_device"
        
        with patch.object(mock_bridge, '_send') as mock_send:
            mock_send.return_value = AsyncMock()
            
            await mock_bridge.cmd_register_app(mock_local_uuid, device_name, mock_pin)
            
            mock_send.assert_called_once_with(
                zehnder_pb2.RegisterAppRequest,
                zehnder_pb2.GatewayOperation.RegisterAppRequestType,
                {
                    "uuid": bytes.fromhex(mock_local_uuid),
                    "devicename": device_name,
                    "pin": int(mock_pin),
                },
            )
    
    @pytest.mark.asyncio
    async def test_cmd_deregister_app(self, mock_bridge, mock_local_uuid):
        """Test app deregistration command."""
        with patch.object(mock_bridge, '_send') as mock_send:
            mock_send.return_value = AsyncMock()
            
            await mock_bridge.cmd_deregister_app(mock_local_uuid)
            
            mock_send.assert_called_once_with(
                zehnder_pb2.DeregisterAppRequest,
                zehnder_pb2.GatewayOperation.DeregisterAppRequestType,
                {"uuid": bytes.fromhex(mock_local_uuid)},
            )
    
    @pytest.mark.asyncio
    async def test_cmd_deregister_self_raises_error(self, mock_bridge):
        """Test deregistering self raises SelfDeregistrationError."""
        mock_bridge._local_uuid = "test_uuid"
        
        with pytest.raises(SelfDeregistrationError):
            await mock_bridge.cmd_deregister_app("test_uuid")
    
    @pytest.mark.asyncio
    async def test_cmd_start_session(self, mock_bridge):
        """Test start session command."""
        with patch.object(mock_bridge, '_send') as mock_send:
            mock_send.return_value = AsyncMock()
            
            await mock_bridge.cmd_start_session()
            
            mock_send.assert_called_once_with(
                zehnder_pb2.StartSessionRequest,
                zehnder_pb2.GatewayOperation.StartSessionRequestType,
                {"takeover": False},
            )
    
    @pytest.mark.asyncio
    async def test_cmd_close_session(self, mock_bridge):
        """Test close session command."""
        with patch.object(mock_bridge, '_send') as mock_send:
            mock_send.return_value = AsyncMock()
            
            await mock_bridge.cmd_close_session()
            
            mock_send.assert_called_once_with(
                zehnder_pb2.CloseSessionRequest,
                zehnder_pb2.GatewayOperation.CloseSessionRequestType,
                reply=False,
            )
    
    @pytest.mark.asyncio
    async def test_cmd_keepalive(self, mock_bridge):
        """Test keepalive command."""
        with patch.object(mock_bridge, '_send') as mock_send:
            mock_send.return_value = AsyncMock()
            
            await mock_bridge.cmd_keepalive()
            
            mock_send.assert_called_once_with(
                zehnder_pb2.KeepAlive,
                zehnder_pb2.GatewayOperation.KeepAliveType,
                reply=False,
            )
    
    @pytest.mark.asyncio
    async def test_send_not_connected_raises_error(self, mock_bridge):
        """Test sending message when not connected raises error."""
        with pytest.raises(AioComfoConnectNotConnected):
            await mock_bridge._send(
                zehnder_pb2.KeepAlive,
                zehnder_pb2.GatewayOperation.KeepAliveType,
                {},
            )
    
    @pytest.mark.asyncio
    async def test_send_timeout_raises_error(self, mock_bridge):
        """Test sending message with timeout raises error."""
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = False
        mock_writer.write = MagicMock()
        mock_writer.drain = AsyncMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()
        
        mock_bridge._writer = mock_writer
        mock_bridge._event_bus = EventBus()
        mock_bridge._reference = 0
        
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            with pytest.raises(AioComfoConnectTimeout):
                await mock_bridge._send(
                    zehnder_pb2.KeepAlive,
                    zehnder_pb2.GatewayOperation.KeepAliveType,
                    {},
                )


class TestMessage:
    """Test Message class."""
    
    def test_init(self):
        """Test Message initialization."""
        cmd = zehnder_pb2.GatewayOperation()
        msg = zehnder_pb2.KeepAlive()
        src = "00000000000000000000000000000001"
        dst = "00000000000000000000000000000002"
        message = Message(cmd, msg, src, dst)
        
        assert message.cmd == cmd
        assert message.msg == msg
        assert message.src == src
        assert message.dst == dst
    
    def test_str(self):
        """Test Message string representation."""
        cmd = zehnder_pb2.GatewayOperation()
        msg = zehnder_pb2.KeepAlive()
        src = "00000000000000000000000000000001"
        dst = "00000000000000000000000000000002"
        message = Message(cmd, msg, src, dst)
        
        str_repr = str(message)
        assert src in str_repr
        assert dst in str_repr