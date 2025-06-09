"""ComfoConnect Bridge API abstraction

This module provides the ComfoConnect class, an abstraction layer over the Zehnder ComfoConnect LAN C API.
It manages connection, sensor registration, property access, and provides high-level methods for controlling
and monitoring the ventilation system.

Classes:
    ComfoConnect: Main class for managing a connection to a ComfoConnect bridge device and interacting with sensors and properties.

Example:
    from aiocomfoconnect.comfoconnect import ComfoConnect
    comfo = ComfoConnect(host, uuid)
    await comfo.connect(local_uuid)
    ...
"""

from __future__ import annotations

import asyncio
import logging
from asyncio import Future
from typing import Callable, Dict, List, Literal, Any

from aiocomfoconnect import Bridge
from aiocomfoconnect.const import (
    ERRORS,
    ERRORS_140,
    SUBUNIT_01,
    SUBUNIT_02,
    SUBUNIT_03,
    SUBUNIT_05,
    SUBUNIT_06,
    SUBUNIT_07,
    SUBUNIT_08,
    UNIT_ERROR,
    UNIT_SCHEDULE,
    UNIT_TEMPHUMCONTROL,
    UNIT_VENTILATIONCONFIG,
    ComfoCoolMode,
    PdoType,
    VentilationBalance,
    VentilationMode,
    VentilationSetting,
    VentilationSpeed,
    VentilationTemperatureProfile,
)
from aiocomfoconnect.exceptions import (
    AioComfoConnectNotConnected,
    AioComfoConnectTimeout,
    ComfoConnectNotAllowed,
)
from aiocomfoconnect.properties import Property
from aiocomfoconnect.sensors import Sensor
from aiocomfoconnect.util import bytearray_to_bits, bytestring, encode_pdo_value

_LOGGER = logging.getLogger(__name__)

class ComfoConnect(Bridge):
    """
    Abstraction layer over the ComfoConnect LAN C API.

    This class manages the connection to a ComfoConnect bridge device, handles sensor registration,
    property access, and provides high-level methods for controlling and monitoring the ventilation system.
    """

    # RMI Command Types (private to class)
    _CMD_GET_PROPERTY = 0x01
    _CMD_GET_MULTIPLE_PROPERTIES = 0x02
    _CMD_SET_PROPERTY = 0x03
    _CMD_CLEAR_ERRORS = 0x82
    _CMD_GET_MODE = 0x83
    _CMD_SET_MODE = 0x84
    _CMD_ENABLE_MODE = 0x85

    def __init__(self, host: str, uuid: str, loop=None, sensor_callback=None, alarm_callback=None, sensor_delay=2):
        """
        Initialize the ComfoConnect class.

        Args:
            host (str): The IP address or hostname of the bridge.
            uuid (str): The UUID to use for registration.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use. Defaults to None.
            sensor_callback (Callable, optional): Callback for sensor updates. Defaults to None.
            alarm_callback (Callable, optional): Callback for alarm updates. Defaults to None.
            sensor_delay (int, optional): Delay in seconds before emitting sensor values after connect. Defaults to 2.
        """
        super().__init__(host, uuid, loop)

        self.set_sensor_callback(self._sensor_callback)  # Set the callback to our _sensor_callback method, so we can proces the callbacks.
        self.set_alarm_callback(self._alarm_callback)  # Set the callback to our _alarm_callback method, so we can proces the callbacks.
        self.sensor_delay = sensor_delay

        self._sensor_callback_fn: Callable = sensor_callback
        self._alarm_callback_fn: Callable = alarm_callback
        self._sensors: Dict[int, Sensor] = {}
        self._sensors_values: Dict[int, any] = {}
        self._sensor_hold = None

        self._tasks = set()

    def _unhold_sensors(self):
        """
        Unhold the sensors and emit cached sensor values.
        """
        _LOGGER.debug("Unholding sensors")
        self._sensor_hold = None
        for sensor_id, _ in self._sensors.items():
            if self._sensors_values.get(sensor_id) is not None:
                self._sensor_callback(sensor_id, self._sensors_values.get(sensor_id))

    async def connect(self, uuid: str):
        """
        Connect to the bridge and start the session. Handles reconnection logic.

        Args:
            uuid (str): The UUID to use for registration.
        """
        connected: Future = Future()

        async def _reconnect_loop():
            while True:
                try:
                    read_task = await self._connect(uuid)
                    await self.cmd_start_session(True)

                    # Wait for a specified amount of seconds to buffer sensor values.
                    # This is to work around a bug where the bridge sends invalid sensor values when connecting.
                    if self.sensor_delay:
                        _LOGGER.debug("Holding sensors for %s second(s)", self.sensor_delay)
                        self._sensors_values = {}
                        self._sensor_hold = self._loop.call_later(self.sensor_delay, self._unhold_sensors)

                    # Register the sensors again (in case we lost the connection)
                    for sensor in self._sensors.values():
                        await self.cmd_rpdo_request(sensor.id, sensor.type)
                    if not connected.done():
                        connected.set_result(True)
                    await read_task
                    if read_task.result() is False:
                        # We are shutting down.
                        return
                except AioComfoConnectTimeout:
                    _LOGGER.info("Could not reconnect. Retrying after 5 seconds.")
                    await asyncio.sleep(5)
                except AioComfoConnectNotConnected:
                    _LOGGER.info("We got disconnected. Reconnecting.")
                except ComfoConnectNotAllowed as exception:
                    # Passthrough exception if not allowed (because not registered uuid for example )
                    connected.set_exception(exception)
                    return

        reconnect_task = self._loop.create_task(_reconnect_loop())
        self._tasks.add(reconnect_task)
        reconnect_task.add_done_callback(self._tasks.discard)
        await connected

    async def disconnect(self):
        """
        Disconnect from the bridge.
        """
        await self._disconnect()

    async def register_sensor(self, sensor: Sensor):
        """
        Register a sensor on the bridge.

        Args:
            sensor (Sensor): The sensor to register.
        """
        self._sensors[sensor.id] = sensor
        self._sensors_values[sensor.id] = None
        await self.cmd_rpdo_request(sensor.id, sensor.type)

    async def deregister_sensor(self, sensor: Sensor):
        """
        Deregister a sensor on the bridge.

        Args:
            sensor (Sensor): The sensor to deregister.
        """
        await self.cmd_rpdo_request(sensor.id, sensor.type, timeout=0)
        del self._sensors[sensor.id]
        del self._sensors_values[sensor.id]

    async def get_property(self, prop: Property, node_id=1) -> any:
        """
        Get a property and convert to the right type.

        Args:
            prop (Property): The property to get.
            node_id (int, optional): The node ID. Defaults to 1.
        Returns:
            Any: The property value, type depends on property_type.
        """
        return await self.get_single_property(prop.unit, prop.subunit, prop.property_id, prop.property_type, node_id=node_id)

    async def get_single_property(
        self,
        unit: int,
        subunit: int,
        property_id: int,
        property_type: int | None = None,
        node_id: int = 1
    ) -> Any:
        """Get a property and convert to the correct type.

        Args:
            unit (int): The unit ID.
            subunit (int): The subunit ID.
            property_id (int): The property ID.
            property_type (int | None): The property type.
            node_id (int): The node ID. Defaults to 1.
        Returns:
            Any: The property value, type depends on property_type.
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, unit, subunit, 0x10, property_id]), node_id=node_id)
        match property_type:
            case PdoType.TYPE_CN_STRING:
                return result.message.decode("utf-8").rstrip("\x00")
            case PdoType.TYPE_CN_INT8 | PdoType.TYPE_CN_INT16 | PdoType.TYPE_CN_INT64:
                return int.from_bytes(result.message, byteorder="little", signed=True)
            case PdoType.TYPE_CN_UINT8 | PdoType.TYPE_CN_UINT16 | PdoType.TYPE_CN_UINT32:
                return int.from_bytes(result.message, byteorder="little", signed=False)
            case PdoType.TYPE_CN_BOOL:
                return result.message[0] == 1
            case _:
                return result.message

    async def get_multiple_properties(self, unit: int, subunit: int, property_ids: List[int], node_id=1) -> Any:
        """
        Get multiple properties.

        Args:
            unit (int): The unit ID.
            subunit (int): The subunit ID.
            property_ids (List[int]): List of property IDs.
            node_id (int, optional): The node ID. Defaults to 1.
        Returns:
            Any: The result message.
        """
        result = await self.cmd_rmi_request(bytestring([self._CMD_GET_MULTIPLE_PROPERTIES, unit, subunit, 0x01, 0x10 | len(property_ids), bytes(property_ids)]), node_id=node_id)
        return result.message

    async def set_property(self, unit: int, subunit: int, property_id: int, value: int, node_id=1) -> Any:
        """
        Set a property.

        Args:
            unit (int): The unit ID.
            subunit (int): The subunit ID.
            property_id (int): The property ID.
            value (int): The value to set.
            node_id (int, optional): The node ID. Defaults to 1.
        Returns:
            Any: The result message.
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, unit, subunit, property_id, value]), node_id=node_id)
        return result.message

    async def set_property_typed(self, unit: int, subunit: int, property_id: int, value: int, pdo_type: PdoType, node_id=1) -> Any:
        """
        Set a typed property.

        Args:
            unit (int): The unit ID.
            subunit (int): The subunit ID.
            property_id (int): The property ID.
            value (int): The value to set.
            pdo_type (PdoType): The PDO type.
            node_id (int, optional): The node ID. Defaults to 1.
        Returns:
            Any: The result message.
        """
        value_bytes = encode_pdo_value(value, pdo_type)
        message_bytes = bytes([self._CMD_SET_PROPERTY, unit, subunit, property_id]) + value_bytes
        result = await self.cmd_rmi_request(message_bytes, node_id=node_id)
        return result.message

    async def clear_errors(self):
        """Clear the errors."""
        await self.cmd_rmi_request(bytes([self._CMD_CLEAR_ERRORS, UNIT_ERROR, SUBUNIT_01]))

    def _sensor_callback(self, sensor_id: int, sensor_value: Any) -> None:
        """Handle sensor updates and invoke the user callback.

        Args:
            sensor_id (int): The sensor ID.
            sensor_value (Any): The sensor value.
        """
        if self._sensor_callback_fn is None:
            return

        sensor = self._sensors.get(sensor_id)
        if sensor is None:
            _LOGGER.error(f"Unknown sensor id: {sensor_id}")
            return

        self._sensors_values[sensor_id] = sensor_value

        # Don't emit sensor values until we have received all the initial values.
        if self._sensor_hold is not None:
            return

        val = sensor.value_fn(sensor_value) if sensor.value_fn else round(sensor_value, 2)
        self._sensor_callback_fn(sensor, val)

    def _alarm_callback(self, node_id: int, alarm: Any) -> None:
        """Handle alarm updates and invoke the user callback.

        Args:
            node_id (int): The node ID.
            alarm (Any): The alarm object.
        """
        if self._alarm_callback_fn is None:
            return

        error_messages = ERRORS_140 if getattr(alarm, 'swProgramVersion', 0) <= 3222278144 else ERRORS
        errors = {bit: error_messages[bit] for bit in bytearray_to_bits(getattr(alarm, 'errors', b''))}
        self._alarm_callback_fn(node_id, errors)

    async def get_mode(self) -> str:
        """Get the current ventilation mode.

        Returns:
            str: The current mode ("manual" or "auto").
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_08, 0x01]))
        # 0000000000ffffffff0000000001 = auto
        # 0100000000ffffffffffffffff01 = manual
        mode = result.message[0]
        return VentilationMode.MANUAL if mode == 1 else VentilationMode.AUTO

    async def set_mode(self, mode: Literal["auto", "manual"]) -> None:
        """Set the ventilation mode (auto / manual).

        Args:
            mode (Literal["auto", "manual"]): The desired mode.
        Raises:
            ValueError: If the mode is invalid.
        """
        if mode == VentilationMode.AUTO:
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_08, 0x01]))
        elif mode == VentilationMode.MANUAL:
            await self.cmd_rmi_request(bytes([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_speed_enum(self) -> VentilationSpeed:
        """Get the current ventilation speed as an enum.

        Returns:
            VentilationSpeed: The current speed (AWAY, LOW, MEDIUM, HIGH).
        Raises:
            ValueError: If the speed is invalid.
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x01]))
        speed = result.message[-1]
        try:
            return VentilationSpeed(speed)
        except ValueError:
            raise ValueError(f"Invalid speed: {speed}")

    async def get_speed(self) -> str:
        """Backwards-compatible: Get the current ventilation speed as a string ('away', 'low', 'medium', 'high')."""
        speed_enum = await self.get_speed_enum()
        return str(speed_enum)

    async def set_speed_enum(self, speed: VentilationSpeed) -> None:
        """Set the ventilation speed using the enum (AWAY, LOW, MEDIUM, HIGH)."""
        if not isinstance(speed, VentilationSpeed):
            raise ValueError(f"Invalid speed: {speed}")
        await self.cmd_rmi_request(bytes([
            self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x01,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, speed.value
        ]))

    async def set_speed(self, speed: str) -> None:
        """Backwards-compatible: Set the ventilation speed using a string ('away', 'low', 'medium', 'high')."""
        try:
            speed_enum = VentilationSpeed[speed.strip().upper()]
        except KeyError:
            try:
                speed_enum = VentilationSpeed(int(speed))
            except Exception:
                raise ValueError(f"Invalid speed: {speed}")
        await self.set_speed_enum(speed_enum)

    async def get_flow_for_speed(self, speed: Literal["away", "low", "medium", "high"]) -> int:
        """
        Get the targeted airflow in m³/h for the given VentilationSpeed.

        Args:
            speed (Literal["away", "low", "medium", "high"]): The speed to query.
        Returns:
            int: The targeted airflow in m³/h.
        """
        match speed:
            case VentilationSpeed.AWAY:
                property_id = 3
            case VentilationSpeed.LOW:
                property_id = 4
            case VentilationSpeed.MEDIUM:
                property_id = 5
            case VentilationSpeed.HIGH:
                property_id = 6

        return await self.get_single_property(UNIT_VENTILATIONCONFIG, SUBUNIT_01, property_id, PdoType.TYPE_CN_INT16)

    async def set_flow_for_speed(self, speed: Literal["away", "low", "medium", "high"], desired_flow: int):
        """
        Set the targeted airflow in m³/h for the given VentilationSpeed.

        Args:
            speed (Literal["away", "low", "medium", "high"]): The speed to set.
            desired_flow (int): The desired airflow in m³/h.
        """
        match speed:
            case VentilationSpeed.AWAY:
                property_id = 3
            case VentilationSpeed.LOW:
                property_id = 4
            case VentilationSpeed.MEDIUM:
                property_id = 5
            case VentilationSpeed.HIGH:
                property_id = 6

        await self.set_property_typed(UNIT_VENTILATIONCONFIG, SUBUNIT_01, property_id, desired_flow, PdoType.TYPE_CN_INT16)

    async def get_bypass(self):
        """Get the bypass mode (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_02, 0x01]))
        # 0000000000080700000000000000 = auto
        # 0100000000100e00000b0e000001 = open
        # 0100000000100e00000d0e000002 = close
        mode = result.message[-1]
        match mode:
            case 0:
                return VentilationSetting.AUTO
            case 1:
                return VentilationSetting.ON
            case 2:
                return VentilationSetting.OFF
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def set_bypass(self, mode: Literal["auto", "on", "off"], timeout: int = -1) -> None:
        """Set the bypass mode (auto / on / off)."""
        if mode == VentilationSetting.AUTO:
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_02, 0x01]))
        elif mode == VentilationSetting.ON:
            await self.cmd_rmi_request(bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_02, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
        elif mode == VentilationSetting.OFF:
            await self.cmd_rmi_request(bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_02, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x02]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_balance_mode(self) -> str:
        """Get the ventilation balance mode (balance / supply only / exhaust only)."""
        result_06 = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
        result_07 = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
        # result_06:
        # 0000000000080700000000000001 = balance
        # 0100000000100e00000e0e000001 = supply only
        # 0000000000080700000000000001 = exhaust only

        # result_07:
        # 0000000000080700000000000001 = balance
        # 0000000000080700000000000001 = supply only
        # 0100000000100e00000e0e000001 = exhaust only
        mode_06 = result_06.message[0]
        mode_07 = result_07.message[0]
        if mode_06 == mode_07:
            return VentilationBalance.BALANCE
        if mode_06 == 1 and mode_07 == 0:
            return VentilationBalance.SUPPLY_ONLY
        if mode_06 == 0 and mode_07 == 1:
            return VentilationBalance.EXHAUST_ONLY
        raise ValueError(f"Invalid mode: 6={mode_06}, 7={mode_07}")

    async def set_balance_mode(self, mode: Literal["balance", "supply_only", "exhaust_only"], timeout: int = -1) -> None:
        """Set the ventilation balance mode (balance / supply only / exhaust only)."""
        if mode == VentilationBalance.BALANCE:
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
        elif mode == VentilationBalance.SUPPLY_ONLY:
            await self.cmd_rmi_request(bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
        elif mode == VentilationBalance.EXHAUST_ONLY:
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
            await self.cmd_rmi_request(bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_boost(self) -> bool:
        """Get boost mode."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x06]))
        # 0000000000580200000000000003 = not active
        # 0100000000580200005602000003 = active
        mode = result.message[0]
        return mode == 1

    async def set_boost(self, mode: bool, timeout: int = 3600) -> None:
        """Activate boost mode."""
        if mode:
            await self.cmd_rmi_request(bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x06, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x03]))
        else:
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x06]))

    async def get_away(self) -> bool:
        """Get away mode."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x0B]))
        # 0000000000b00400000000000000 = not active
        # 0100000000550200005302000000 = active
        mode = result.message[0]
        return mode == 1

    async def set_away(self, mode: bool, timeout: int = 3600) -> None:
        """Activate away mode."""
        if mode:
            await self.cmd_rmi_request(bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x0B, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x00]))
        else:
            await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_01, 0x0B]))

    async def get_comfocool_mode_enum(self) -> ComfoCoolMode:
        """Get the current ComfoCool mode as an enum.

        Returns:
            ComfoCoolMode: The current mode (AUTO, OFF).
        Raises:
            ValueError: If the mode is invalid.
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_05, 0x01]))
        mode = result.message[0]
        try:
            return ComfoCoolMode(mode)
        except ValueError:
            raise ValueError(f"Invalid ComfoCool mode: {mode}")

    async def get_comfocool_mode(self) -> str:
        """Backwards-compatible: Get the current ComfoCool mode as a string ('auto', 'off')."""
        mode_enum = await self.get_comfocool_mode_enum()
        return str(mode_enum)

    async def set_comfocool_mode_enum(self, mode: ComfoCoolMode, timeout: int = -1) -> None:
        """Set the ComfoCool mode using the enum (AUTO, OFF)."""
        if not isinstance(mode, ComfoCoolMode):
            raise ValueError(f"Invalid ComfoCool mode: {mode}")
        await self.cmd_rmi_request(bytes([
            self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_05, 0x01,
            0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), mode.value
        ]))

    async def set_comfocool_mode(self, mode: str, timeout: int = -1) -> None:
        """Backwards-compatible: Set the ComfoCool mode using a string ('auto', 'off')."""
        try:
            mode_enum = ComfoCoolMode[mode.strip().upper()]
        except KeyError:
            try:
                mode_enum = ComfoCoolMode(int(mode))
            except Exception:
                raise ValueError(f"Invalid ComfoCool mode: {mode}")
        await self.set_comfocool_mode_enum(mode_enum, timeout)

    async def get_temperature_profile_enum(self) -> VentilationTemperatureProfile:
        """
        Asynchronously retrieve the current temperature profile setting of the ventilation unit.
        Returns:
            VentilationTemperatureProfile: The current temperature profile (WARM, NORMAL, COOL)
        Raises:
            ValueError: If the received mode value is not recognized.
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_03, 0x01]))
    
        mode = result.message[-1]
        try:
            return VentilationTemperatureProfile(mode)
        except ValueError:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_temperature_profile(self) -> str:
        """Backwards-compatible: Get the temperature profile as a string ('warm', 'normal', 'cool')."""
        profile = await self.get_temperature_profile_enum()
        return str(profile)

    async def set_temperature_profile_enum(self, profile: VentilationTemperatureProfile, timeout: int = -1) -> None:
        """Set the temperature profile (warm / normal / cool)."""
        if not isinstance(profile, VentilationTemperatureProfile):
            raise ValueError(f"Invalid profile: {profile}")
        await self.cmd_rmi_request(bytestring([
            self._CMD_SET_MODE,
            UNIT_SCHEDULE,
            SUBUNIT_03,
            0x01,
            0x00, 0x00, 0x00, 0x00,
            timeout.to_bytes(4, "little", signed=True),
            profile.value
        ]))

    async def set_temperature_profile(self, profile: str, timeout: int = -1) -> None:
        """Backwards-compatible: Set the temperature profile using a string ('warm', 'normal', 'cool')."""
        try:
            # Try by name (string)
            enum_profile = VentilationTemperatureProfile[profile.strip().upper()]
        except KeyError:
            try:
                # Try by int value
                enum_profile = VentilationTemperatureProfile(int(profile))
            except Exception:    
                raise ValueError(f"Invalid temperature profile: {profile}")
        await self.set_temperature_profile_enum(enum_profile, timeout)

    async def get_sensor_ventmode_temperature_passive(self) -> str:
        """Get sensor based ventilation mode - temperature passive (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x04]))
        mode = int.from_bytes(result.message, "little")
        match mode:
            case 1:
                return VentilationSetting.AUTO
            case 2:
                return VentilationSetting.ON
            case 0:
                return VentilationSetting.OFF
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def set_sensor_ventmode_temperature_passive(self, mode: Literal["auto", "on", "off"]) -> None:
        """Configure sensor based ventilation mode - temperature passive (auto / on / off)."""
        match mode:
            case VentilationSetting.AUTO:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, 0x01]))
            case VentilationSetting.ON:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, 0x02]))
            case VentilationSetting.OFF:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, 0x00]))
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def get_sensor_ventmode_humidity_comfort(self) -> str:
        """Get sensor based ventilation mode - humidity comfort (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x06]))
        mode = int.from_bytes(result.message, "little")
        match mode:
            case 1:
                return VentilationSetting.AUTO
            case 2:
                return VentilationSetting.ON
            case 0:
                return VentilationSetting.OFF
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def set_sensor_ventmode_humidity_comfort(self, mode: Literal["auto", "on", "off"]) -> None:
        """Configure sensor based ventilation mode - humidity comfort (auto / on / off)."""
        match mode:
            case VentilationSetting.AUTO:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, 0x01]))
            case VentilationSetting.ON:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, 0x02]))
            case VentilationSetting.OFF:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, 0x00]))
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def get_sensor_ventmode_humidity_protection(self) -> str:
        """Get sensor based ventilation mode - humidity protection (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x07]))
        mode = int.from_bytes(result.message, "little")
        match mode:
            case 1:
                return VentilationSetting.AUTO
            case 2:
                return VentilationSetting.ON
            case 0:
                return VentilationSetting.OFF
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def set_sensor_ventmode_humidity_protection(self, mode: Literal["auto", "on", "off"]) -> None:
        """Configure sensor-based ventilation mode - humidity protection.

        Args:
            mode (Literal["auto", "on", "off"]): Desired mode.

        Raises:
            ValueError: If the mode is invalid.
        """
        match mode:
            case VentilationSetting.AUTO:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, 0x01]))
            case VentilationSetting.ON:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, 0x02]))
            case VentilationSetting.OFF:
                await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, 0x00]))
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def clear_errors(self):
        """Clear the errors."""
        await self.cmd_rmi_request(bytes([self._CMD_CLEAR_ERRORS, UNIT_ERROR, SUBUNIT_01]))
