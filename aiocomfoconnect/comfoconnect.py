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
from typing import Callable, Dict, List, Literal

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

    async def get_single_property(self, unit: int, subunit: int, property_id: int, property_type: int = None, node_id=1) -> any:
        """
        Get a property and convert to the right type.

        Args:
            unit (int): The unit ID.
            subunit (int): The subunit ID.
            property_id (int): The property ID.
            property_type (int): The property type.
            node_id (int, optional): The node ID. Defaults to 1.
        Returns:
            Any: The property value, type depends on property_type.
        """
        result = await self.cmd_rmi_request(bytes([0x01, unit, subunit, 0x10, property_id]), node_id=node_id)

        if property_type == PdoType.TYPE_CN_STRING:
            return result.message.decode("utf-8").rstrip("\x00")
        if property_type in [PdoType.TYPE_CN_INT8, PdoType.TYPE_CN_INT16, PdoType.TYPE_CN_INT64]:
            return int.from_bytes(result.message, byteorder="little", signed=True)
        if property_type in [PdoType.TYPE_CN_UINT8, PdoType.TYPE_CN_UINT16, PdoType.TYPE_CN_UINT32]:
            return int.from_bytes(result.message, byteorder="little", signed=False)
        if property_type in [PdoType.TYPE_CN_BOOL]:
            return result.message[0] == 1

        return result.message

    async def get_multiple_properties(self, unit: int, subunit: int, property_ids: List[int], node_id=1) -> any:
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
        result = await self.cmd_rmi_request(bytestring([0x02, unit, subunit, 0x01, 0x10 | len(property_ids), bytes(property_ids)]), node_id=node_id)

        return result.message

    async def set_property(self, unit: int, subunit: int, property_id: int, value: int, node_id=1) -> any:
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
        result = await self.cmd_rmi_request(bytes([0x03, unit, subunit, property_id, value]), node_id=node_id)

        return result.message

    async def set_property_typed(self, unit: int, subunit: int, property_id: int, value: int, pdo_type: PdoType, node_id=1) -> any:
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
        message_bytes = bytes([0x03, unit, subunit, property_id]) + value_bytes

        result = await self.cmd_rmi_request(message_bytes, node_id=node_id)

        return result.message

    def _sensor_callback(self, sensor_id, sensor_value):
        """
        Callback function for sensor updates.

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

        if sensor.value_fn:
            val = sensor.value_fn(sensor_value)
        else:
            val = round(sensor_value, 2)
        self._sensor_callback_fn(sensor, val)

    def _alarm_callback(self, node_id, alarm):
        """
        Callback function for alarm updates.

        Args:
            node_id (int): The node ID.
            alarm (Any): The alarm object.
        """
        if self._alarm_callback_fn is None:
            return

        if alarm.swProgramVersion <= 3222278144:
            # Firmware 1.4.0 and below
            error_messages = ERRORS_140
        else:
            error_messages = ERRORS

        errors = {bit: error_messages[bit] for bit in bytearray_to_bits(alarm.errors)}
        self._alarm_callback_fn(node_id, errors)

    async def get_mode(self):
        """
        Get the current ventilation mode.

        Returns:
            str: The current mode ("manual" or "auto").
        """
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_08, 0x01]))
        # 0000000000ffffffff0000000001 = auto
        # 0100000000ffffffffffffffff01 = manual
        mode = result.message[0]

        return VentilationMode.MANUAL if mode == 1 else VentilationMode.AUTO

    async def set_mode(self, mode: Literal["auto", "manual"]):
        """
        Set the ventilation mode (auto / manual).

        Args:
            mode (Literal["auto", "manual"]): The desired mode.
        Raises:
            ValueError: If the mode is invalid.
        """
        if mode == VentilationMode.AUTO:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_08, 0x01]))
        elif mode == VentilationMode.MANUAL:
            await self.cmd_rmi_request(bytes([0x84, UNIT_SCHEDULE, SUBUNIT_08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_speed(self):
        """
        Get the current ventilation speed.

        Returns:
            str: The current speed ("away", "low", "medium", "high").
        Raises:
            ValueError: If the speed is invalid.
        """
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_01, 0x01]))
        # 0100000000ffffffffffffffff00 = away
        # 0100000000ffffffffffffffff01 = low
        # 0100000000ffffffffffffffff02 = medium
        # 0100000000ffffffffffffffff03 = high
        speed = result.message[-1]

        if speed == 0:
            return VentilationSpeed.AWAY
        if speed == 1:
            return VentilationSpeed.LOW
        if speed == 2:
            return VentilationSpeed.MEDIUM
        if speed == 3:
            return VentilationSpeed.HIGH

        raise ValueError(f"Invalid speed: {speed}")

    async def set_speed(self, speed: Literal["away", "low", "medium", "high"]):
        """
        Set the ventilation speed (away / low / medium / high).

        Args:
            speed (Literal["away", "low", "medium", "high"]): The desired speed.
        Raises:
            ValueError: If the speed is invalid.
        """
        if speed == VentilationSpeed.AWAY:
            await self.cmd_rmi_request(bytes([0x84, UNIT_SCHEDULE, SUBUNIT_01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
        elif speed == VentilationSpeed.LOW:
            await self.cmd_rmi_request(bytes([0x84, UNIT_SCHEDULE, SUBUNIT_01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01]))
        elif speed == VentilationSpeed.MEDIUM:
            await self.cmd_rmi_request(bytes([0x84, UNIT_SCHEDULE, SUBUNIT_01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x02]))
        elif speed == VentilationSpeed.HIGH:
            await self.cmd_rmi_request(bytes([0x84, UNIT_SCHEDULE, SUBUNIT_01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x03]))
        else:
            raise ValueError(f"Invalid speed: {speed}")

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
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_02, 0x01]))
        # 0000000000080700000000000000 = auto
        # 0100000000100e00000b0e000001 = open
        # 0100000000100e00000d0e000002 = close
        mode = result.message[-1]

        if mode == 0:
            return VentilationSetting.AUTO
        if mode == 1:
            return VentilationSetting.ON
        if mode == 2:
            return VentilationSetting.OFF

        raise ValueError(f"Invalid mode: {mode}")

    async def set_bypass(self, mode: Literal["auto", "on", "off"], timeout=-1):
        """Set the bypass mode (auto / on / off)."""
        if mode == VentilationSetting.AUTO:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_02, 0x01]))
        elif mode == VentilationSetting.ON:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_02, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
        elif mode == VentilationSetting.OFF:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_02, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x02]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_balance_mode(self):
        """Get the ventilation balance mode (balance / supply only / exhaust only)."""
        result_06 = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
        result_07 = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
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

    async def set_balance_mode(self, mode: Literal["balance", "supply_only", "exhaust_only"], timeout=-1):
        """Set the ventilation balance mode (balance / supply only / exhaust only)."""
        if mode == VentilationBalance.BALANCE:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
        elif mode == VentilationBalance.SUPPLY_ONLY:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_06, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_07, 0x01]))
        elif mode == VentilationBalance.EXHAUST_ONLY:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_06, 0x01]))
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_07, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_boost(self):
        """Get boost mode."""
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_01, 0x06]))
        # 0000000000580200000000000003 = not active
        # 0100000000580200005602000003 = active
        mode = result.message[0]

        return mode == 1

    async def set_boost(self, mode: bool, timeout=3600):
        """Activate boost mode."""
        if mode:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_01, 0x06, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x03]))
        else:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_01, 0x06]))

    async def get_away(self):
        """Get away mode."""
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_01, 0x0B]))
        # 0000000000b00400000000000000 = not active
        # 0100000000550200005302000000 = active
        mode = result.message[0]

        return mode == 1

    async def set_away(self, mode: bool, timeout=3600):
        """Activate away mode."""
        if mode:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_01, 0x0B, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x00]))
        else:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_01, 0x0B]))

    async def get_comfocool_mode(self):
        """Get the current comfocool mode."""
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_05, 0x01]))
        mode = result.message[0]
        return mode == 0

    async def set_comfocool_mode(self, mode: Literal["auto", "off"], timeout=-1):
        """
        Set the ComfoCool mode to either 'auto' or 'off'.

        Args:
            mode (Literal["auto", "off"]): The desired ComfoCool mode. 
                - "auto": Enables automatic ComfoCool mode.
                - "off": Disables ComfoCool mode.
            timeout (int, optional): Timeout value in seconds for the 'off' mode. 
                Defaults to -1. Only used when mode is "off".

        Raises:
            ValueError: If an invalid mode is provided.

        Note:
            This method sends the appropriate command to the device to change the ComfoCool mode.
        """
        
        if mode == ComfoCoolMode.AUTO:
            await self.cmd_rmi_request(bytes([0x85, UNIT_SCHEDULE, SUBUNIT_05, 0x01]))
        elif mode == ComfoCoolMode.OFF:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_05, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x00]))

    async def get_temperature_profile(self):
        """
        Asynchronously retrieves the current temperature profile setting of the ventilation unit.
        Returns:
            VentilationTemperatureProfile: The current temperature profile, which can be one of:
                - VentilationTemperatureProfile.WARM: Warm profile
                - VentilationTemperatureProfile.NORMAL: Normal profile
                - VentilationTemperatureProfile.COOL: Cool profile
        Raises:
            ValueError: If the received mode value is not recognized.
        """
        
        result = await self.cmd_rmi_request(bytes([0x83, UNIT_SCHEDULE, SUBUNIT_03, 0x01]))
        # 0100000000ffffffffffffffff02 = warm
        # 0100000000ffffffffffffffff00 = normal
        # 0100000000ffffffffffffffff01 = cool
        mode = result.message[-1]

        if mode == 2:
            return VentilationTemperatureProfile.WARM
        if mode == 0:
            return VentilationTemperatureProfile.NORMAL
        if mode == 1:
            return VentilationTemperatureProfile.COOL

        raise ValueError(f"Invalid mode: {mode}")

    async def set_temperature_profile(self, profile: Literal["warm", "normal", "cool"], timeout=-1):
        """Set the temperature profile (warm / normal / cool)."""
        if profile == VentilationTemperatureProfile.WARM:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_03, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x02]))
        elif profile == VentilationTemperatureProfile.NORMAL:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_03, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x00]))
        elif profile == VentilationTemperatureProfile.COOL:
            await self.cmd_rmi_request(bytestring([0x84, UNIT_SCHEDULE, SUBUNIT_03, 0x01, 0x00, 0x00, 0x00, 0x00, timeout.to_bytes(4, "little", signed=True), 0x01]))
        else:
            raise ValueError(f"Invalid profile: {profile}")

    async def get_sensor_ventmode_temperature_passive(self):
        """Get sensor based ventilation mode - temperature passive (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([0x01, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x04]))
        # 00 = off
        # 01 = auto
        # 02 = on
        mode = int.from_bytes(result.message, "little")

        if mode == 1:
            return VentilationSetting.AUTO
        if mode == 2:
            return VentilationSetting.ON
        if mode == 0:
            return VentilationSetting.OFF

        raise ValueError(f"Invalid mode: {mode}")

    async def set_sensor_ventmode_temperature_passive(self, mode: Literal["auto", "on", "off"]):
        """Configure sensor based ventilation mode - temperature passive (auto / on / off)."""
        if mode == VentilationSetting.AUTO:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, 0x01]))
        elif mode == VentilationSetting.ON:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, 0x02]))
        elif mode == VentilationSetting.OFF:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x04, 0x00]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_sensor_ventmode_humidity_comfort(self):
        """Get sensor based ventilation mode - humidity comfort (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([0x01, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x06]))
        # 00 = off
        # 01 = auto
        # 02 = on
        mode = int.from_bytes(result.message, "little")

        if mode == 1:
            return VentilationSetting.AUTO
        if mode == 2:
            return VentilationSetting.ON
        if mode == 0:
            return VentilationSetting.OFF

        raise ValueError(f"Invalid mode: {mode}")

    async def set_sensor_ventmode_humidity_comfort(self, mode: Literal["auto", "on", "off"]):
        """Configure sensor based ventilation mode - humidity comfort (auto / on / off)."""
        if mode == VentilationSetting.AUTO:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, 0x01]))
        elif mode == VentilationSetting.ON:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, 0x02]))
        elif mode == VentilationSetting.OFF:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x06, 0x00]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def get_sensor_ventmode_humidity_protection(self):
        """Get sensor based ventilation mode - humidity protection (auto / on / off)."""
        result = await self.cmd_rmi_request(bytes([0x01, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x10, 0x07]))
        # 00 = off
        # 01 = auto
        # 02 = on
        mode = int.from_bytes(result.message, "little")

        if mode == 1:
            return VentilationSetting.AUTO
        if mode == 2:
            return VentilationSetting.ON
        if mode == 0:
            return VentilationSetting.OFF

        raise ValueError(f"Invalid mode: {mode}")

    async def set_sensor_ventmode_humidity_protection(self, mode: Literal["auto", "on", "off"]):
        """Configure sensor based ventilation mode - humidity protection (auto / on / off)."""
        if mode == VentilationSetting.AUTO:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, 0x01]))
        elif mode == VentilationSetting.ON:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, 0x02]))
        elif mode == VentilationSetting.OFF:
            await self.cmd_rmi_request(bytes([0x03, UNIT_TEMPHUMCONTROL, SUBUNIT_01, 0x07, 0x00]))
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def clear_errors(self):
        """Clear the errors."""
        await self.cmd_rmi_request(bytes([0x82, UNIT_ERROR, 0x01]))
