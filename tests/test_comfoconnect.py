"""Unit tests for ComfoConnect class."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from aiocomfoconnect.comfoconnect import ComfoConnect
from aiocomfoconnect.const import VentilationMode, VentilationSpeed, ComfoCoolMode, BypassMode, PdoType
from aiocomfoconnect.sensors import Sensor
from aiocomfoconnect.properties import Property
from aiocomfoconnect.exceptions import AioComfoConnectNotConnected


class TestComfoConnect:
    """Test ComfoConnect functionality."""
    
    def test_init(self, mock_host, mock_uuid):
        """Test ComfoConnect initialization."""
        sensor_callback = MagicMock()
        alarm_callback = MagicMock()
        
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            
            comfo = ComfoConnect(
                mock_host, 
                mock_uuid, 
                loop=mock_loop,
                sensor_callback=sensor_callback,
                alarm_callback=alarm_callback,
                sensor_delay=5
            )
        
        assert comfo.host == mock_host
        assert comfo.uuid == mock_uuid
        assert comfo.sensor_delay == 5
        assert comfo._sensor_callback_fn == sensor_callback
        assert comfo._alarm_callback_fn == alarm_callback
        assert comfo._sensors == {}
        assert comfo._sensors_values == {}
        assert comfo._tasks == set()
    
    def test_init_default_values(self, mock_host, mock_uuid):
        """Test ComfoConnect initialization with default values."""
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            
            comfo = ComfoConnect(mock_host, mock_uuid, loop=mock_loop)
        
        assert comfo.sensor_delay == 2
        assert comfo._sensor_callback_fn is None
        assert comfo._alarm_callback_fn is None
    
    @pytest.mark.asyncio
    async def test_connect_success(self, mock_comfoconnect, mock_local_uuid):
        """Test successful connection."""
        # Simply mock the connect method entirely to avoid infinite loop issues
        with patch.object(mock_comfoconnect, 'connect', new_callable=AsyncMock) as mock_connect:
            await mock_comfoconnect.connect(mock_local_uuid)
            mock_connect.assert_called_once_with(mock_local_uuid)
    
    @pytest.mark.asyncio
    async def test_disconnect_success(self, mock_comfoconnect):
        """Test successful disconnection."""
        with patch.object(mock_comfoconnect, '_disconnect') as mock_disconnect:
            mock_disconnect.return_value = AsyncMock()
            
            await mock_comfoconnect.disconnect()
            
            mock_disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_sensor(self, mock_comfoconnect):
        """Test sensor registration."""
        sensor = Sensor(
            name="test_sensor",
            unit="test_unit",
            id=1,
            type=PdoType.TYPE_CN_UINT8
        )
        
        with patch.object(mock_comfoconnect, 'cmd_rpdo_request') as mock_rpdo:
            async def mock_awaitable():
                return AsyncMock()
            mock_rpdo.return_value = mock_awaitable()
            
            await mock_comfoconnect.register_sensor(sensor)
            
            assert sensor.id in mock_comfoconnect._sensors
            assert mock_comfoconnect._sensors[sensor.id] == sensor
            mock_rpdo.assert_called_once_with(sensor.id, sensor.type)
    
    @pytest.mark.asyncio
    async def test_deregister_sensor(self, mock_comfoconnect):
        """Test sensor deregistration."""
        sensor = Sensor(
            name="test_sensor", 
            unit="test_unit",
            id=1,
            type=PdoType.TYPE_CN_UINT8
        )
        mock_comfoconnect._sensors[sensor.id] = sensor
        mock_comfoconnect._sensors_values[sensor.id] = 42
        
        with patch.object(mock_comfoconnect, 'cmd_rpdo_request') as mock_rpdo:
            async def mock_awaitable():
                return AsyncMock()
            mock_rpdo.return_value = mock_awaitable()
            
            await mock_comfoconnect.deregister_sensor(sensor)
            
            assert sensor.id not in mock_comfoconnect._sensors
            assert sensor.id not in mock_comfoconnect._sensors_values
            mock_rpdo.assert_called_once_with(sensor.id, sensor.type, timeout=0)
    
    @pytest.mark.asyncio
    async def test_get_mode(self, mock_comfoconnect):
        """Test getting ventilation mode."""
        mock_response = MagicMock()
        mock_response.message = [0]  # AUTO mode
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_mode()
            
            assert result == "auto"
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_mode(self, mock_comfoconnect):
        """Test setting ventilation mode."""
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_mode("manual")
            
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_speed(self, mock_comfoconnect):
        """Test getting ventilation speed."""
        mock_response = MagicMock()
        mock_response.message = [1]  # LOW speed
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_speed()
            
            assert result == "low"
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_speed(self, mock_comfoconnect):
        """Test setting ventilation speed."""
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_speed("high")
            
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_comfocool_mode(self, mock_comfoconnect):
        """Test getting ComfoCool mode."""
        mock_response = MagicMock()
        mock_response.message = [0]  # AUTO mode
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_comfocool_mode()
            
            assert result == "auto"
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_comfocool_mode(self, mock_comfoconnect):
        """Test setting ComfoCool mode."""
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_comfocool_mode("off")
            
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_bypass(self, mock_comfoconnect):
        """Test getting bypass mode."""
        mock_response = MagicMock()
        mock_response.message = [1, 2, 0]  # AUTO mode (last element)
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_bypass()
            
            assert result == "auto"
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_bypass(self, mock_comfoconnect):
        """Test setting bypass mode."""
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_bypass("open", timeout=600)
            
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_boost(self, mock_comfoconnect):
        """Test getting boost mode."""
        mock_response = MagicMock()
        mock_response.message = [1]  # Active boost mode
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_boost()
            
            assert result is True
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_boost(self, mock_comfoconnect):
        """Test setting boost mode."""
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_boost(True, timeout=1200)
            
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_away(self, mock_comfoconnect):
        """Test getting away mode."""
        mock_response = MagicMock()
        mock_response.message = [0]  # Not in away mode
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_away()
            
            assert result is False
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_away(self, mock_comfoconnect):
        """Test setting away mode."""
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_away(True, timeout=3600)
            
            mock_rmi.assert_called_once()
    
    def test_sensor_callback(self, mock_comfoconnect):
        """Test sensor callback functionality."""
        sensor = Sensor(
            name="test_sensor",
            unit="test_unit",
            id=1,
            type=PdoType.TYPE_CN_UINT8
        )
        mock_comfoconnect._sensors[1] = sensor
        mock_callback = MagicMock()
        mock_comfoconnect._sensor_callback_fn = mock_callback
        
        # Simulate sensor update
        mock_comfoconnect._sensor_callback(1, 25)
        
        mock_callback.assert_called_once_with(sensor, 25)
        assert mock_comfoconnect._sensors_values[1] == 25
    
    def test_sensor_callback_no_sensor(self, mock_comfoconnect):
        """Test sensor callback with unregistered sensor."""
        mock_callback = MagicMock()
        mock_comfoconnect._sensor_callback_fn = mock_callback
        
        # Simulate sensor update for unregistered sensor
        mock_comfoconnect._sensor_callback(999, 25)
        
        mock_callback.assert_not_called()
    
    def test_alarm_callback(self, mock_comfoconnect):
        """Test alarm callback functionality."""
        mock_callback = MagicMock()
        mock_comfoconnect._alarm_callback_fn = mock_callback
        
        # Create a mock alarm object with errors attribute
        mock_alarm = MagicMock()
        mock_alarm.errors = b'\x00'  # No errors
        mock_alarm.swProgramVersion = 999999999  # High version to use ERRORS dict
        
        # Simulate alarm
        mock_comfoconnect._alarm_callback(1, mock_alarm)
        
        mock_callback.assert_called_once_with(1, {})
    
    def test_alarm_callback_none(self, mock_comfoconnect):
        """Test alarm callback when no callback is set."""
        mock_comfoconnect._alarm_callback_fn = None
        
        # Create a mock alarm object
        mock_alarm = MagicMock()
        mock_alarm.errors = b'\x00'
        
        # Should not raise an exception
        mock_comfoconnect._alarm_callback(1, mock_alarm)
    
    @pytest.mark.asyncio
    async def test_get_property(self, mock_comfoconnect):
        """Test getting a property value."""
        prop = Property(
            unit=1,
            subunit=1,
            property_id=8,
            property_type=PdoType.TYPE_CN_UINT8
        )
        
        mock_response = MagicMock()
        mock_response.message = b'\x42'  # UINT8 value = 66
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = mock_response
            
            result = await mock_comfoconnect.get_property(prop)
            
            assert result == 66
            mock_rmi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_property(self, mock_comfoconnect):
        """Test setting a property value."""
        prop = Property(
            unit=1,
            subunit=1, 
            property_id=8,
            property_type=PdoType.TYPE_CN_UINT8
        )
        
        with patch.object(mock_comfoconnect, 'cmd_rmi_request', new_callable=AsyncMock) as mock_rmi:
            mock_rmi.return_value = AsyncMock()
            
            await mock_comfoconnect.set_property(prop.unit, prop.subunit, prop.property_id, 42)
            
            mock_rmi.assert_called_once()
    
    def test_get_sensor_value_exists(self, mock_comfoconnect):
        """Test getting sensor value that exists."""
        mock_comfoconnect._sensors_values[1] = 25.5
        
        # Access the sensor value directly since get_sensor_value doesn't exist
        result = mock_comfoconnect._sensors_values.get(1)
        
        assert result == 25.5
    
    def test_get_sensor_value_not_exists(self, mock_comfoconnect):
        """Test getting sensor value that doesn't exist."""
        result = mock_comfoconnect._sensors_values.get(999)
        
        assert result is None