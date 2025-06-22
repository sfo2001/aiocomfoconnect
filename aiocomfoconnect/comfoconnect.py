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

import asyncio
import logging
from enum import Enum
from typing import Any, Callable, List

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
    AirflowSpeed,
    BypassMode,
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


def _convert_to_enum(value: str | int, enum_class: type[Enum], context: str) -> Enum:
    """Convert string or int value to enum.

    Args:
        value: The value to convert (string name or int value)
        enum_class: The enum class to convert to
        context: Context for error message (e.g., "mode", "speed")

    Returns:
        The enum value

    Raises:
        ValueError: If value cannot be converted to enum
    """
    # Handle int values directly
    if isinstance(value, int):
        try:
            return enum_class(value)
        except ValueError as exc:
            raise ValueError(f"Invalid {context}: {value}") from exc

    # Handle string values
    value_str = str(value).strip().upper()
    try:
        # Try by name first (e.g., 'AUTO' -> VentilationMode.AUTO)
        return enum_class[value_str]
    except KeyError:
        try:
            # Try by int value (e.g., '0' -> VentilationMode(0))
            return enum_class(int(value))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid {context}: {value}") from exc


class ComfoConnect(Bridge):
    """
    Provide an abstraction layer over the ComfoConnect LAN C API.

    This class manages the connection to a ComfoConnect bridge device, handles sensor registration,
    property access, and provides high-level methods for controlling and monitoring the ventilation system.

    Attributes:
        sensor_delay (int): Delay in seconds before emitting sensor values after connect.
        _sensor_callback_fn (Callable[[Sensor, Any], None] | None): Callback for sensor updates.
        _alarm_callback_fn (Callable[[int, Any], None] | None): Callback for alarm updates.
        _sensors (dict[int, Sensor]): Registered sensors.
        _sensors_values (dict[int, Any]): Cached sensor values.
        _sensor_hold (Any): Internal hold state for sensors.
        _tasks (set[asyncio.Task[Any]]): Set of running asyncio tasks.
    """

    # RMI Command Types (private to class)
    _CMD_GET_PROPERTY = 0x01
    _CMD_GET_MULTIPLE_PROPERTIES = 0x02
    _CMD_SET_PROPERTY = 0x03
    _CMD_CLEAR_ERRORS = 0x82
    _CMD_GET_MODE = 0x83
    _CMD_SET_MODE = 0x84
    _CMD_ENABLE_MODE = 0x85

    def __init__(
        self,
        host: str,
        uuid: str,
        loop: asyncio.AbstractEventLoop | None = None,
        sensor_callback: Callable[[Sensor, Any], None] | None = None,
        alarm_callback: Callable[[int, Any], None] | None = None,
        sensor_delay: int = 2,
    ) -> None:
        """
        Initialize the ComfoConnect class.

        Args:
            host (str): The IP address or hostname of the bridge.
            uuid (str): The UUID to use for registration.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use. Defaults to None.
            sensor_callback (Callable[[Sensor, Any], None], optional): Callback for sensor updates. Defaults to None.
            alarm_callback (Callable[[int, Any], None], optional): Callback for alarm updates. Defaults to None.
            sensor_delay (int, optional): Delay in seconds before emitting sensor values after connect. Defaults to 2.
        """
        super().__init__(host, uuid, loop)
        self.set_sensor_callback(self._sensor_callback)
        self.set_alarm_callback(self._alarm_callback)
        self.sensor_delay = sensor_delay
        self._sensor_callback_fn: Callable[[Sensor, Any], None] | None = sensor_callback
        self._alarm_callback_fn: Callable[[int, Any], None] | None = alarm_callback
        self._sensors: dict[int, Sensor] = {}
        self._sensors_values: dict[int, Any] = {}
        self._sensor_hold = None
        self._tasks: set[asyncio.Task[Any]] = set()

    def _unhold_sensors(self) -> None:
        """
        Unhold the sensors and emit cached sensor values.
        """
        _LOGGER.debug("Unholding sensors")
        self._sensor_hold = None
        for sensor_id, _ in self._sensors.items():
            if self._sensors_values.get(sensor_id) is not None:
                self._sensor_callback(sensor_id, self._sensors_values.get(sensor_id))

    async def connect(self, uuid: str) -> None:
        """
        Connect to the bridge and start the session. Handle reconnection logic.

        Args:
            uuid (str): The UUID to use for registration.
        """
        connected: asyncio.Future[bool] = asyncio.Future()
        reconnect_task = self._create_reconnection_task(uuid, connected)
        self._register_task(reconnect_task)
        await connected

    def _create_reconnection_task(self, uuid: str, connected: asyncio.Future[bool]) -> asyncio.Task[None]:
        """
        Create and return the reconnection task.

        Args:
            uuid (str): The UUID to use for registration.
            connected (asyncio.Future[bool]): Future to signal when initially connected.

        Returns:
            asyncio.Task[None]: The reconnection task.
        """
        return self._loop.create_task(self._reconnection_loop(uuid, connected))

    def _register_task(self, task: asyncio.Task[None]) -> None:
        """
        Register a task for lifecycle management.

        Args:
            task (asyncio.Task[None]): The task to register.
        """
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _reconnection_loop(self, uuid: str, connected: asyncio.Future[bool]) -> None:
        """
        Handle reconnection attempts with retry logic.

        Args:
            uuid (str): The UUID to use for registration.
            connected (asyncio.Future[bool]): Future to signal when initially connected.
        """
        while True:
            try:
                should_shutdown = await self._establish_connection_session(uuid, connected)
                if should_shutdown:
                    return
            except AioComfoConnectTimeout:
                await self._handle_connection_timeout()
            except AioComfoConnectNotConnected:
                self._handle_disconnection()
            except ComfoConnectNotAllowed as exception:
                self._handle_not_allowed_exception(connected, exception)
                return

    async def _establish_connection_session(self, uuid: str, connected: asyncio.Future[bool]) -> bool:
        """
        Establish connection and setup session.

        Args:
            uuid (str): The UUID to use for registration.
            connected (asyncio.Future[bool]): Future to signal when initially connected.

        Returns:
            bool: True if should shutdown, False to continue reconnection loop.
        """
        read_task = await self._connect(uuid)
        await self.cmd_start_session(True)

        await self._setup_sensor_buffering()
        await self._reregister_sensors()

        self._mark_connected_if_needed(connected)
        await read_task

        return read_task.result() is False  # False result means shutdown

    async def _setup_sensor_buffering(self) -> None:
        """
        Setup sensor value buffering to work around bridge bug.

        This is to work around a bug where the bridge sends invalid sensor values when connecting.
        """
        if self.sensor_delay:
            _LOGGER.debug("Holding sensors for %s second(s)", self.sensor_delay)
            self._sensors_values = {}
            self._sensor_hold = self._loop.call_later(self.sensor_delay, self._unhold_sensors)

    async def _reregister_sensors(self) -> None:
        """
        Re-register all sensors (in case we lost the connection).
        """
        for sensor in self._sensors.values():
            await self.cmd_rpdo_request(sensor.id, sensor.type)

    def _mark_connected_if_needed(self, connected: asyncio.Future[bool]) -> None:
        """
        Mark the connection as established if not already done.

        Args:
            connected (asyncio.Future[bool]): Future to signal when initially connected.
        """
        if not connected.done():
            connected.set_result(True)

    async def _handle_connection_timeout(self) -> None:
        """
        Handle connection timeout by waiting before retry.
        """
        _LOGGER.info("Could not reconnect. Retrying after 5 seconds.")
        await asyncio.sleep(5)

    def _handle_disconnection(self) -> None:
        """
        Handle disconnection event.
        """
        _LOGGER.info("We got disconnected. Reconnecting.")

    def _handle_not_allowed_exception(self, connected: asyncio.Future[bool], exception: ComfoConnectNotAllowed) -> None:
        """
        Handle not allowed exception by propagating it.

        Args:
            connected (asyncio.Future[bool]): Future to signal connection result.
            exception (ComfoConnectNotAllowed): The exception to propagate.
        """
        connected.set_exception(exception)

    async def disconnect(self) -> None:
        """
        Disconnect from the bridge.
        """
        await self._disconnect()

    # Generic RMI Command Helpers

    async def _get_mode_value(self, subunit: int, extra_param: int = 0x01) -> int:
        """Generic helper for GET_MODE commands.

        Args:
            subunit (int): The subunit to query
            extra_param (int): Additional parameter (default 0x01)

        Returns:
            int: The mode value from the response
        """
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, subunit, extra_param]))
        return result.message[0] if len(result.message) == 1 else result.message[-1]

    async def _enable_mode(self, subunit: int, extra_param: int = 0x01) -> None:
        """Generic helper for ENABLE_MODE commands.

        Args:
            subunit (int): The subunit to enable
            extra_param (int): Additional parameter (default 0x01)
        """
        await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, subunit, extra_param]))

    async def _set_mode_with_timeout(self, subunit: int, mode_value: int, timeout: int, extra_param: int = 0x01) -> None:
        """Generic helper for SET_MODE commands with timeout.

        Args:
            subunit (int): The subunit to set
            mode_value (int): The mode value to set
            timeout (int): Timeout value in seconds
            extra_param (int): Additional parameter (default 0x01)
        """
        await self.cmd_rmi_request(
            bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, subunit, extra_param, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), mode_value])
        )

    async def _set_mode_simple(self, subunit: int, mode_value: int, extra_param: int = 0x01) -> None:
        """Generic helper for simple SET_MODE commands.

        Args:
            subunit (int): The subunit to set
            mode_value (int): The mode value to set
            extra_param (int): Additional parameter (default 0x01)
        """
        await self.cmd_rmi_request(bytes([self._CMD_SET_MODE, UNIT_SCHEDULE, subunit, extra_param, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, mode_value]))

    async def _get_enum_value(self, enum_class: type[Enum], subunit: int, context: str, extra_param: int = 0x01) -> Enum:
        """Generic helper to get enum values.

        Args:
            enum_class (type[Enum]): The enum class to convert to
            subunit (int): The subunit to query
            context (str): Context for error messages
            extra_param (int): Additional parameter (default 0x01)

        Returns:
            Enum: The enum value

        Raises:
            ValueError: If the mode value is invalid
        """
        mode = await self._get_mode_value(subunit, extra_param)
        try:
            return enum_class(mode)
        except ValueError as exc:
            raise ValueError(f"Invalid {context}: {mode}") from exc

    async def _get_boolean_value(self, subunit: int, extra_param: int) -> bool:
        """Generic helper to get boolean values.

        Args:
            subunit (int): The subunit to query
            extra_param (int): Additional parameter

        Returns:
            bool: True if mode == 1, False otherwise
        """
        mode = await self._get_mode_value(subunit, extra_param)
        return mode == 1

    async def _set_boolean_mode(self, subunit: int, extra_param: int, mode: bool, timeout: int, mode_value: int) -> None:
        """Generic helper for boolean mode setting.

        Args:
            subunit (int): The subunit to set
            extra_param (int): Additional parameter
            mode (bool): True to activate, False to enable/disable
            timeout (int): Timeout value in seconds
            mode_value (int): Value to set when activating
        """
        if mode:
            await self._set_mode_with_timeout(subunit, mode_value, timeout, extra_param)
        else:
            await self._enable_mode(subunit, extra_param)

    async def register_sensor(self, sensor: Sensor) -> None:
        """
        Register a sensor on the bridge.

        Args:
            sensor (Sensor): The sensor to register.
        """
        self._sensors[sensor.id] = sensor
        self._sensors_values[sensor.id] = None
        await self.cmd_rpdo_request(sensor.id, sensor.type)

    async def deregister_sensor(self, sensor: Sensor) -> None:
        """
        Deregister a sensor on the bridge.

        Args:
            sensor (Sensor): The sensor to deregister.
        """
        await self.cmd_rpdo_request(sensor.id, sensor.type, timeout=0)
        del self._sensors[sensor.id]
        del self._sensors_values[sensor.id]

    async def get_property(self, prop: Property, node_id: int = 1) -> Any:
        """
        Get a property and convert to the right type.

        Args:
            prop (Property): The property to get.
            node_id (int, optional): The node ID. Defaults to 1.
        Returns:
            Any: The property value, type depends on property_type.
        """
        return await self.get_single_property(prop.unit, prop.subunit, prop.property_id, prop.property_type, node_id=node_id)

    async def get_single_property(self, unit: int, subunit: int, property_id: int, property_type: int | None = None, node_id: int = 1) -> Any:
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

    async def get_multiple_properties(self, unit: int, subunit: int, property_ids: List[int], node_id: int = 1) -> Any:
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

    async def set_property(self, unit: int, subunit: int, property_id: int, value: int, node_id: int = 1) -> Any:
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

    async def set_property_typed(self, unit: int, subunit: int, property_id: int, value: int, pdo_type: PdoType, node_id: int = 1) -> Any:
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
            _LOGGER.error("Unknown sensor id: %s", sensor_id)
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

        error_messages = ERRORS_140 if getattr(alarm, "swProgramVersion", 0) <= 3222278144 else ERRORS
        errors = {bit: error_messages[bit] for bit in bytearray_to_bits(getattr(alarm, "errors", b""))}
        self._alarm_callback_fn(node_id, errors)

    async def get_mode_enum(self) -> VentilationMode:
        """Get the current ventilation mode as an enum (AUTO or MANUAL)."""
        return await self._get_enum_value(VentilationMode, SUBUNIT_08, "mode")

    async def get_mode(self) -> str:
        """Backwards-compatible: Get the current ventilation mode as a string ('auto' or 'manual')."""
        mode_enum = await self.get_mode_enum()
        return str(mode_enum)

    async def set_mode_enum(self, mode: VentilationMode) -> None:
        """Set the ventilation mode using the enum (AUTO or MANUAL)."""
        if not isinstance(mode, VentilationMode):
            raise ValueError(f"Invalid mode: {mode}")
        match mode:
            case VentilationMode.AUTO:
                await self._enable_mode(SUBUNIT_08)
            case VentilationMode.MANUAL:
                await self._set_mode_simple(SUBUNIT_08, 0x01)
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def set_mode(self, mode: str) -> None:
        """Backwards-compatible: Set the ventilation mode using a string ('auto' or 'manual')."""
        mode_enum = _convert_to_enum(mode, VentilationMode, "mode")
        await self.set_mode_enum(mode_enum)

    async def get_speed_enum(self) -> VentilationSpeed:
        """Get the current ventilation speed as an enum.

        Returns:
            VentilationSpeed: The current speed (AWAY, LOW, MEDIUM, HIGH).
        Raises:
            ValueError: If the speed is invalid.
        """
        return await self._get_enum_value(VentilationSpeed, SUBUNIT_01, "speed")

    async def get_speed(self) -> str:
        """Backwards-compatible: Get the current ventilation speed as a string ('away', 'low', 'medium', 'high')."""
        speed_enum = await self.get_speed_enum()
        return str(speed_enum)

    async def set_speed_enum(self, speed: VentilationSpeed) -> None:
        """Set the ventilation speed using the enum (AWAY, LOW, MEDIUM, HIGH)."""
        if not isinstance(speed, VentilationSpeed):
            raise ValueError(f"Invalid speed: {speed}")
        await self._set_mode_simple(SUBUNIT_01, speed.value)

    async def set_speed(self, speed: str) -> None:
        """Backwards-compatible: Set the ventilation speed using a string ('away', 'low', 'medium', 'high')."""
        speed_enum = _convert_to_enum(speed, VentilationSpeed, "speed")
        await self.set_speed_enum(speed_enum)

    async def get_flow_for_speed_enum(self, speed: AirflowSpeed) -> int:
        """
        Get the targeted airflow in m³/h for the given AirflowSpeed enum.

        Args:
            speed (AirflowSpeed): The speed to query (AWAY, LOW, MEDIUM, HIGH).
        Returns:
            int: The targeted airflow in m³/h.
        """
        return await self.get_single_property(UNIT_VENTILATIONCONFIG, SUBUNIT_01, speed.value, PdoType.TYPE_CN_INT16)

    async def get_flow_for_speed(self, speed: str) -> int:
        """
        Backwards-compatible: Get the targeted airflow in m³/h for the given speed as a string ('away', 'low', 'medium', 'high').
        """
        speed_enum = _convert_to_enum(speed, AirflowSpeed, "airflow speed")
        return await self.get_flow_for_speed_enum(speed_enum)

    async def set_flow_for_speed_enum(self, speed: AirflowSpeed, desired_flow: int):
        """
        Set the targeted airflow in m³/h for the given AirflowSpeed enum.

        Args:
            speed (AirflowSpeed): The speed to set (AWAY, LOW, MEDIUM, HIGH).
            desired_flow (int): The desired airflow in m³/h.
        """
        await self.set_property_typed(UNIT_VENTILATIONCONFIG, SUBUNIT_01, speed.value, desired_flow, PdoType.TYPE_CN_INT16)

    async def set_flow_for_speed(self, speed: str, desired_flow: int):
        """
        Backwards-compatible: Set the targeted airflow in m³/h for the given speed as a string ('away', 'low', 'medium', 'high').
        """
        speed_enum = _convert_to_enum(speed, AirflowSpeed, "airflow speed")
        await self.set_flow_for_speed_enum(speed_enum, desired_flow)

    async def get_bypass_enum(self) -> BypassMode:
        """Get the bypass mode as an enum (AUTO / OPEN / CLOSED)."""
        return await self._get_enum_value(BypassMode, SUBUNIT_02, "bypass mode")

    async def get_bypass(self) -> str:
        """Backwards-compatible: Get the bypass mode as a string ('auto', 'open', 'closed')."""
        mode_enum = await self.get_bypass_enum()
        return str(mode_enum)

    async def set_bypass_enum(self, mode: BypassMode, timeout: int = -1) -> None:
        """Set the bypass mode using the enum (AUTO / OPEN / CLOSED)."""
        if not isinstance(mode, BypassMode):
            raise ValueError(f"Invalid bypass mode: {mode}")
        match mode:
            case BypassMode.AUTO:
                await self._enable_mode(SUBUNIT_02)
            case BypassMode.OPEN:
                await self._set_mode_with_timeout(SUBUNIT_02, 0x01, timeout)
            case BypassMode.CLOSED:
                await self._set_mode_with_timeout(SUBUNIT_02, 0x02, timeout)

    async def set_bypass(self, mode: str, timeout: int = -1) -> None:
        """Backwards-compatible: Set the bypass mode using a string ('auto', 'open', 'closed').
        Accepts deprecated 'on' (as 'open') and 'off' (as 'closed')."""
        mode_str = mode.strip().lower()
        if mode_str == "on":
            _LOGGER.warning("Bypass mode 'on' is deprecated, use 'open' instead.")
            mode_str = "open"
        elif mode_str == "off":
            _LOGGER.warning("Bypass mode 'off' is deprecated, use 'closed' instead.")
            mode_str = "closed"
        mode_enum = _convert_to_enum(mode_str, BypassMode, "bypass mode")
        await self.set_bypass_enum(mode_enum, timeout)

    async def get_balance_mode_enum(self) -> VentilationBalance:
        """Get the ventilation balance mode as an enum (BALANCE, SUPPLY_ONLY, EXHAUST_ONLY).

        Returns:
            VentilationBalance: The current balance mode.
        Raises:
            ValueError: If the mode combination is invalid.
        """
        result_06 = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
        result_07 = await self.cmd_rmi_request(bytes([self._CMD_GET_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
        mode_06 = result_06.message[0]
        mode_07 = result_07.message[0]
        try:
            return VentilationBalance.from_subunits(mode_06, mode_07)
        except ValueError as e:
            raise ValueError(f"Invalid mode: 6={mode_06}, 7={mode_07}") from e

    async def get_balance_mode(self) -> str:
        """Backwards-compatible: Get the ventilation balance mode as a string ('balance', 'supply_only', 'exhaust_only')."""
        mode_enum = await self.get_balance_mode_enum()
        return str(mode_enum)

    async def set_balance_mode_enum(self, mode: VentilationBalance, timeout: int = -1) -> None:
        """Set the ventilation balance mode using the enum (BALANCE, SUPPLY_ONLY, EXHAUST_ONLY).

        Args:
            mode (VentilationBalance): The desired balance mode.
            timeout (int, optional): Timeout in seconds. Defaults to -1.
        Raises:
            ValueError: If the mode is invalid.
        """
        match mode:
            case VentilationBalance.BALANCE:
                await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
                await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
            case VentilationBalance.SUPPLY_ONLY:
                await self.cmd_rmi_request(
                    bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01])
                )
                await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
            case VentilationBalance.EXHAUST_ONLY:
                await self.cmd_rmi_request(bytes([self._CMD_ENABLE_MODE, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
                await self.cmd_rmi_request(
                    bytestring([self._CMD_SET_MODE, UNIT_SCHEDULE, SUBUNIT_07, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01])
                )
            case _:
                raise ValueError(f"Invalid mode: {mode}")

    async def set_balance_mode(self, mode: str, timeout: int = -1) -> None:
        """Backwards-compatible: Set the ventilation balance mode using a string ('balance', 'supply_only', 'exhaust_only')."""
        mode_enum = _convert_to_enum(mode, VentilationBalance, "balance mode")
        await self.set_balance_mode_enum(mode_enum, timeout)

    async def get_boost(self) -> bool:
        """Get boost mode."""
        return await self._get_boolean_value(SUBUNIT_01, 0x06)

    async def set_boost(self, mode: bool, timeout: int = 3600) -> None:
        """Activate boost mode."""
        await self._set_boolean_mode(SUBUNIT_01, 0x06, mode, timeout, 0x03)

    async def get_away(self) -> bool:
        """Get away mode."""
        return await self._get_boolean_value(SUBUNIT_01, 0x0B)

    async def set_away(self, mode: bool, timeout: int = 3600) -> None:
        """Activate away mode."""
        await self._set_boolean_mode(SUBUNIT_01, 0x0B, mode, timeout, 0x00)

    async def get_comfocool_mode_enum(self) -> ComfoCoolMode:
        """Get the current ComfoCool mode as an enum.

        Returns:
            ComfoCoolMode: The current mode (AUTO, OFF).
        Raises:
            ValueError: If the mode is invalid.
        """
        return await self._get_enum_value(ComfoCoolMode, SUBUNIT_05, "ComfoCool mode")

    async def get_comfocool_mode(self) -> str:
        """Backwards-compatible: Get the current ComfoCool mode as a string ('auto', 'off')."""
        mode_enum = await self.get_comfocool_mode_enum()
        return str(mode_enum)

    async def set_comfocool_mode_enum(self, mode: ComfoCoolMode, timeout: int = -1) -> None:
        """Set the ComfoCool mode using the enum (AUTO, OFF)."""
        if not isinstance(mode, ComfoCoolMode):
            raise ValueError(f"Invalid ComfoCool mode: {mode}")
        await self._set_mode_with_timeout(SUBUNIT_05, mode.value, timeout)

    async def set_comfocool_mode(self, mode: str, timeout: int = -1) -> None:
        """Backwards-compatible: Set the ComfoCool mode using a string ('auto', 'off')."""
        mode_enum = _convert_to_enum(mode, ComfoCoolMode, "ComfoCool mode")
        await self.set_comfocool_mode_enum(mode_enum, timeout)

    async def get_temperature_profile_enum(self) -> VentilationTemperatureProfile:
        """
        Asynchronously retrieve the current temperature profile setting of the ventilation unit.
        Returns:
            VentilationTemperatureProfile: The current temperature profile (WARM, NORMAL, COOL)
        Raises:
            ValueError: If the received mode value is not recognized.
        """
        return await self._get_enum_value(VentilationTemperatureProfile, SUBUNIT_03, "temperature profile")

    async def get_temperature_profile(self) -> str:
        """Backwards-compatible: Get the temperature profile as a string ('warm', 'normal', 'cool')."""
        profile = await self.get_temperature_profile_enum()
        return str(profile)

    async def set_temperature_profile_enum(self, profile: VentilationTemperatureProfile, timeout: int = -1) -> None:
        """Set the temperature profile (warm / normal / cool)."""
        if not isinstance(profile, VentilationTemperatureProfile):
            raise ValueError(f"Invalid profile: {profile}")
        await self._set_mode_with_timeout(SUBUNIT_03, profile.value, timeout)

    async def set_temperature_profile(self, profile: str, timeout: int = -1) -> None:
        """Backwards-compatible: Set the temperature profile using a string ('warm', 'normal', 'cool')."""
        enum_profile = _convert_to_enum(profile, VentilationTemperatureProfile, "temperature profile")
        await self.set_temperature_profile_enum(enum_profile, timeout)

    async def get_sensor_ventmode_temperature_passive_enum(self) -> VentilationSetting:
        """Get sensor based ventilation mode - temperature passive as enum (AUTO / ON / OFF)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x04]))
        mode = int.from_bytes(result.message, "little")
        try:
            return VentilationSetting(mode)
        except ValueError as exc:
            raise ValueError(f"Invalid mode: {mode}") from exc

    async def get_sensor_ventmode_temperature_passive(self) -> str:
        """Backwards-compatible: Get sensor based ventilation mode - temperature passive as string ('auto', 'on', 'off')."""
        mode_enum = await self.get_sensor_ventmode_temperature_passive_enum()
        return str(mode_enum)

    async def set_sensor_ventmode_temperature_passive_enum(self, mode: VentilationSetting) -> None:
        """Set sensor based ventilation mode - temperature passive using enum (AUTO / ON / OFF)."""
        if not isinstance(mode, VentilationSetting):
            raise ValueError(f"Invalid mode: {mode}")
        await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, mode.value]))

    async def set_sensor_ventmode_temperature_passive(self, mode: str) -> None:
        """Backwards-compatible: Set sensor based ventilation mode - temperature passive using string ('auto', 'on', 'off')."""
        mode_enum = _convert_to_enum(mode, VentilationSetting, "mode")
        await self.set_sensor_ventmode_temperature_passive_enum(mode_enum)

    async def get_sensor_ventmode_humidity_comfort_enum(self) -> VentilationSetting:
        """Get sensor based ventilation mode - humidity comfort as enum (AUTO / ON / OFF)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x06]))
        mode = int.from_bytes(result.message, "little")
        try:
            return VentilationSetting(mode)
        except ValueError as exc:
            raise ValueError(f"Invalid mode: {mode}") from exc

    async def get_sensor_ventmode_humidity_comfort(self) -> str:
        """Backwards-compatible: Get sensor based ventilation mode - humidity comfort as string ('auto', 'on', 'off')."""
        mode_enum = await self.get_sensor_ventmode_humidity_comfort_enum()
        return str(mode_enum)

    async def set_sensor_ventmode_humidity_comfort_enum(self, mode: VentilationSetting) -> None:
        """Set sensor based ventilation mode - humidity comfort using enum (AUTO / ON / OFF)."""
        if not isinstance(mode, VentilationSetting):
            raise ValueError(f"Invalid mode: {mode}")
        await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, mode.value]))

    async def set_sensor_ventmode_humidity_comfort(self, mode: str) -> None:
        """Backwards-compatible: Set sensor based ventilation mode - humidity comfort using string ('auto', 'on', 'off')."""
        mode_enum = _convert_to_enum(mode, VentilationSetting, "mode")
        await self.set_sensor_ventmode_humidity_comfort_enum(mode_enum)

    async def get_sensor_ventmode_humidity_protection_enum(self) -> VentilationSetting:
        """Get sensor based ventilation mode - humidity protection as enum (AUTO / ON / OFF)."""
        result = await self.cmd_rmi_request(bytes([self._CMD_GET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x07]))
        mode = int.from_bytes(result.message, "little")
        try:
            return VentilationSetting(mode)
        except ValueError as exc:
            raise ValueError(f"Invalid mode: {mode}") from exc

    async def get_sensor_ventmode_humidity_protection(self) -> str:
        """Backwards-compatible: Get sensor based ventilation mode - humidity protection as string ('auto', 'on', 'off')."""
        mode_enum = await self.get_sensor_ventmode_humidity_protection_enum()
        return str(mode_enum)

    async def set_sensor_ventmode_humidity_protection_enum(self, mode: VentilationSetting) -> None:
        """Set sensor based ventilation mode - humidity protection using enum (AUTO / ON / OFF)."""
        if not isinstance(mode, VentilationSetting):
            raise ValueError(f"Invalid mode: {mode}")
        await self.cmd_rmi_request(bytes([self._CMD_SET_PROPERTY, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, mode.value]))

    async def set_sensor_ventmode_humidity_protection(self, mode: str) -> None:
        """Backwards-compatible: Set sensor based ventilation mode - humidity protection using string ('auto', 'on', 'off')."""
        mode_enum = _convert_to_enum(mode, VentilationSetting, "mode")
        await self.set_sensor_ventmode_humidity_protection_enum(mode_enum)
