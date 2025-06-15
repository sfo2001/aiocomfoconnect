""" ComfoConnect Bridge API

This module provides the Bridge class for interacting with the Zehnder ComfoConnect LAN C API.
It manages the connection, message sending/receiving, and provides methods for session management,
device registration, and data requests. It also defines the EventBus and Message classes for internal use.

Classes:
    Bridge: Main class for managing a connection to a ComfoConnect bridge device.
    EventBus: Simple event bus for async replies.
    Message: Encapsulates a message sent to/from the bridge.
    SelfDeregistrationError: Exception for self-deregistration attempts.

Exceptions:
    Raises various custom exceptions for connection errors, protocol errors, and invalid operations.

Example:
    from aiocomfoconnect.bridge import Bridge
    bridge = Bridge(host, uuid)
    await bridge._connect(local_uuid)
    ...
"""

from __future__ import annotations

import asyncio
import logging
import struct
from asyncio import StreamReader, StreamWriter
from typing import Awaitable, Callable, Any

from google.protobuf.message import DecodeError
from google.protobuf.message import Message as ProtobufMessage

from .exceptions import (
    AioComfoConnectNotConnected,
    AioComfoConnectTimeout,
    ComfoConnectBadRequest,
    ComfoConnectError,
    ComfoConnectInternalError,
    ComfoConnectNoResources,
    ComfoConnectNotAllowed,
    ComfoConnectNotExist,
    ComfoConnectNotReachable,
    ComfoConnectOtherSession,
    ComfoConnectRmiError,
)
from .protobuf import zehnder_pb2

from aiocomfoconnect.decorators import log_call

_LOGGER = logging.getLogger(__name__)

TIMEOUT: int = 5


class SelfDeregistrationError(Exception):
    """Exception raised when trying to deregister self."""
    pass


class EventBus:
    """An event bus for async replies.

    Attributes:
        listeners (dict[int, set[asyncio.Future]]): Mapping of event references to sets of futures.
    """
    def __init__(self) -> None:
        self.listeners: dict[int, set[asyncio.Future]] = {}

    def add_listener(self, event_name: int, future: asyncio.Future) -> None:
        """Add a listener to the event bus.

        Args:
            event_name (int): The event reference number.
            future (asyncio.Future): The future to be set when the event is emitted.
        """
        _LOGGER.debug(f"Adding listener for event {event_name}")
        if not self.listeners.get(event_name, None):
            self.listeners[event_name] = {future}
        else:
            self.listeners[event_name].add(future)

    def emit(self, event_name: int, event: Any) -> None:
        """Emit an event to the event bus.

        Args:
            event_name (int): The event reference number.
            event (Any): The event object or exception to set on the futures.
        """
        _LOGGER.debug(f"Emitting for event {event_name}")
        futures = self.listeners.get(event_name, set())
        for future in futures:
            if isinstance(event, Exception):
                future.set_exception(event)
            else:
                future.set_result(event)
        if event_name in self.listeners:
            del self.listeners[event_name]


class Bridge:
    """Bridge for interacting with the Zehnder ComfoConnect LAN C API.

    Manages the connection to a ComfoConnect bridge device, handles message sending and receiving,
    and provides methods for session management, device registration, and data requests.

    Attributes:
        host (str): The bridge host address.
        uuid (str): The bridge UUID.
        _local_uuid (str | None): The local UUID for the session.
        _reader (StreamReader | None): The asyncio stream reader.
        _writer (StreamWriter | None): The asyncio stream writer.
        _reference (int | None): The current message reference number.
        _event_bus (EventBus | None): The event bus for async replies.
        __sensor_callback_fn (Callable | None): Callback for sensor messages.
        __alarm_callback_fn (Callable | None): Callback for alarm messages.
        _loop (asyncio.AbstractEventLoop): The event loop in use.
    """
    PORT: int = 56747

    def __init__(self, host: str, uuid: str, loop: asyncio.AbstractEventLoop | None = None) -> None:
        self.host: str = host
        self.uuid: str = uuid
        self._local_uuid: str | None = None
        self._reader: StreamReader | None = None
        self._writer: StreamWriter | None = None
        self._reference: int | None = None
        self._event_bus: EventBus | None = None
        self.__sensor_callback_fn: Callable | None = None
        self.__alarm_callback_fn: Callable | None = None
        self._loop: asyncio.AbstractEventLoop = loop or asyncio.get_running_loop()
        self._read_task: asyncio.Task | None = None

    def __repr__(self) -> str:
        return f"<Bridge {self.host}, UID={self.uuid}>"

    def set_sensor_callback(self, callback: Callable) -> None:
        """Set a callback to be called when a sensor message is received.

        Args:
            callback (Callable): The callback function.
        """
        self.__sensor_callback_fn = callback

    def set_alarm_callback(self, callback: Callable) -> None:
        """Set a callback to be called when an alarm is received.

        Args:
            callback (Callable): The callback function.
        """
        self.__alarm_callback_fn = callback

    async def _connect(self, uuid: str) -> asyncio.Task:
        """Connect to the bridge.

        Args:
            uuid (str): The local UUID to use for the session.

        Returns:
            asyncio.Task: The background task for reading messages.

        Raises:
            AioComfoConnectTimeout: If connection times out.
        """
        _LOGGER.debug(f"Connecting to bridge {self.host}")
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.PORT), TIMEOUT
            )
        except asyncio.TimeoutError as exc:
            _LOGGER.warning(f"Timeout while connecting to bridge {self.host}")
            raise AioComfoConnectTimeout("Timeout while connecting to bridge") from exc

        self._reference = 1
        self._local_uuid = uuid
        self._event_bus = EventBus()

        async def _read_messages() -> None:
            while True:
                try:
                    await self._process_message()
                except asyncio.CancelledError:
                    return
                except AioComfoConnectNotConnected as exc:
                    raise AioComfoConnectNotConnected("We have been disconnected") from exc

        self._read_task = self._loop.create_task(_read_messages())
        _LOGGER.debug(f"Connected to bridge {self.host}")
        return self._read_task

    async def _disconnect(self) -> None:
        """Disconnect from the bridge."""
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._read_task = None

    def is_connected(self) -> bool:
        """Return True if the bridge is connected."""
        return self._writer is not None and not self._writer.is_closing()

    async def _send(
        self,
        request: type[ProtobufMessage],
        request_type: int,
        params: dict[str, Any] | None = None,
        reply: bool = True,
    ) -> Message:
        """Send a command and optionally wait for a response.

        Args:
            request (type[ProtobufMessage]): The protobuf request class.
            request_type (int): The request type enum value.
            params (dict[str, Any] | None): Parameters to set on the request message.
            reply (bool): Whether to wait for a reply.

        Returns:
            Message: The response message.

        Raises:
            AioComfoConnectNotConnected: If not connected.
            AioComfoConnectTimeout: If waiting for a reply times out.
        """
        if not self.is_connected():
            raise AioComfoConnectNotConnected

        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = request_type
        cmd.reference = self._reference

        msg = request()
        if params is not None:
            for param, value in params.items():
                if value is not None:
                    setattr(msg, param, value)

        message = Message(cmd, msg, self._local_uuid or '', self.uuid)

        fut = asyncio.Future()
        if reply:
            self._event_bus.add_listener(self._reference, fut)
        else:
            fut.set_result(None)

        _LOGGER.debug(f"TX {message}")
        self._writer.write(message.encode())
        await self._writer.drain()
        self._reference += 1

        try:
            return await asyncio.wait_for(fut, TIMEOUT)
        except asyncio.TimeoutError as exc:
            _LOGGER.warning("Timeout while waiting for response from bridge")
            await self._disconnect()
            raise AioComfoConnectTimeout("Timeout while waiting for response from bridge") from exc

    async def _read(self) -> Message:
        """Read a message from the bridge and decode it.

        Returns:
            Message: The decoded message.

        Raises:
            ComfoConnectBadRequest: If the bridge returns a BAD_REQUEST.
            ComfoConnectInternalError: If the bridge returns an INTERNAL_ERROR.
            ComfoConnectNotReachable: If the bridge returns NOT_REACHABLE.
            ComfoConnectOtherSession: If the bridge returns OTHER_SESSION.
            ComfoConnectNotAllowed: If the bridge returns NOT_ALLOWED.
            ComfoConnectNoResources: If the bridge returns NO_RESOURCES.
            ComfoConnectNotExist: If the bridge returns NOT_EXIST.
            ComfoConnectRmiError: If the bridge returns RMI_ERROR.
        """
        msg_len_buf = await self._reader.readexactly(4)
        msg_len = int.from_bytes(msg_len_buf, byteorder="big")
        msg_buf = await self._reader.readexactly(msg_len)
        message = Message.decode(msg_buf)
        _LOGGER.debug(f"RX {message}")
        match message.cmd.result:
            case zehnder_pb2.GatewayOperation.OK:
                pass
            case zehnder_pb2.GatewayOperation.BAD_REQUEST:
                raise ComfoConnectBadRequest(message)
            case zehnder_pb2.GatewayOperation.INTERNAL_ERROR:
                raise ComfoConnectInternalError(message)
            case zehnder_pb2.GatewayOperation.NOT_REACHABLE:
                raise ComfoConnectNotReachable(message)
            case zehnder_pb2.GatewayOperation.OTHER_SESSION:
                raise ComfoConnectOtherSession(message)
            case zehnder_pb2.GatewayOperation.NOT_ALLOWED:
                raise ComfoConnectNotAllowed(message)
            case zehnder_pb2.GatewayOperation.NO_RESOURCES:
                raise ComfoConnectNoResources(message)
            case zehnder_pb2.GatewayOperation.NOT_EXIST:
                raise ComfoConnectNotExist(message)
            case zehnder_pb2.GatewayOperation.RMI_ERROR:
                raise ComfoConnectRmiError(message)
        return message

    async def _process_message(self) -> None:
        """Process a message from the bridge."""
        try:
            message = await self._read()
            match message.cmd.type:
                case zehnder_pb2.GatewayOperation.CnRpdoNotificationType:
                    if self.__sensor_callback_fn:
                        self.__sensor_callback_fn(
                            message.msg.pdid,
                            int.from_bytes(message.msg.data, byteorder="little", signed=True),
                        )
                    else:
                        _LOGGER.info("Unhandled CnRpdoNotificationType since no callback is registered.")
                case zehnder_pb2.GatewayOperation.GatewayNotificationType:
                    _LOGGER.debug("Unhandled GatewayNotificationType")
                case zehnder_pb2.GatewayOperation.CnNodeNotificationType:
                    _LOGGER.debug("Unhandled CnNodeNotificationType")
                case zehnder_pb2.GatewayOperation.CnAlarmNotificationType:
                    if self.__alarm_callback_fn:
                        self.__alarm_callback_fn(message.msg.nodeId, message.msg)
                    else:
                        _LOGGER.info("Unhandled CnAlarmNotificationType since no callback is registered.")
                case zehnder_pb2.GatewayOperation.CloseSessionRequestType:
                    _LOGGER.info("The Bridge has asked us to close the connection.")
                case _ if message.cmd.reference:
                    self._event_bus.emit(message.cmd.reference, message.msg)
                case _:
                    _LOGGER.warning(f"Unhandled message type {message.cmd.type}: {message}")
        except asyncio.IncompleteReadError as exc:
            _LOGGER.info("The connection was closed.")
            await self._disconnect()
            raise AioComfoConnectNotConnected("The connection was closed.") from exc
        except ComfoConnectError as exc:
            if exc.message.cmd.reference:
                self._event_bus.emit(exc.message.cmd.reference, exc)
        except DecodeError as exc:
            _LOGGER.error(f"Failed to decode message: {exc}")

    @log_call
    def cmd_start_session(self, take_over: bool = False) -> Awaitable[Message]:
        """Start the session on the device by logging in and optionally disconnecting an existing session.

        Args:
            take_over (bool): Whether to take over an existing session.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.StartSessionRequest,
            zehnder_pb2.GatewayOperation.StartSessionRequestType,
            {"takeover": take_over},
        )

    @log_call
    def cmd_close_session(self) -> Awaitable[Message]:
        """Stop the current session.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.CloseSessionRequest,
            zehnder_pb2.GatewayOperation.CloseSessionRequestType,
            reply=False,
        )

    @log_call
    def cmd_list_registered_apps(self) -> Awaitable[Message]:
        """Return a list of all registered clients.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.ListRegisteredAppsRequest,
            zehnder_pb2.GatewayOperation.ListRegisteredAppsRequestType,
        )

    @log_call
    def cmd_register_app(self, uuid: str, device_name: str, pin: int) -> Awaitable[Message]:
        """Register a new app by specifying uuid, device_name, and pin code.

        Args:
            uuid (str): The UUID of the app to register.
            device_name (str): The device name.
            pin (int): The pin code.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.RegisterAppRequest,
            zehnder_pb2.GatewayOperation.RegisterAppRequestType,
            {
                "uuid": bytes.fromhex(uuid),
                "devicename": device_name,
                "pin": int(pin),
            },
        )

    @log_call
    def cmd_deregister_app(self, uuid: str) -> Awaitable[Message]:
        """Remove the specified app from the registration list.

        Args:
            uuid (str): The UUID of the app to deregister.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.

        Raises:
            SelfDeregistrationError: If attempting to deregister self.
        """
        if uuid == self._local_uuid:
            raise SelfDeregistrationError("You should not deregister yourself.")
        return self._send(
            zehnder_pb2.DeregisterAppRequest,
            zehnder_pb2.GatewayOperation.DeregisterAppRequestType,
            {"uuid": bytes.fromhex(uuid)},
        )

    @log_call
    def cmd_version_request(self) -> Awaitable[Message]:
        """Return version information.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.VersionRequest,
            zehnder_pb2.GatewayOperation.VersionRequestType,
        )

    @log_call
    def cmd_time_request(self) -> Awaitable[Message]:
        """Return the current time on the device.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.CnTimeRequest,
            zehnder_pb2.GatewayOperation.CnTimeRequestType,
        )

    @log_call
    def cmd_rmi_request(self, message: bytes, node_id: int = 1) -> Awaitable[Message]:
        """Send a Remote Method Invocation (RMI) request to a specified node.

        Args:
            message (bytes): The message payload to send with the RMI request.
            node_id (int): The target node ID. Defaults to 1.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.CnRmiRequest,
            zehnder_pb2.GatewayOperation.CnRmiRequestType,
            {"nodeId": node_id or 1, "message": message},
        )

    @log_call
    def cmd_rpdo_request(
        self, pdid: int, pdo_type: int = 1, zone: int = 1, timeout: int | None = None
    ) -> Awaitable[Message]:
        """Register a RPDO request.

        Args:
            pdid (int): The process data object ID.
            pdo_type (int): The PDO type. Defaults to 1.
            zone (int): The zone. Defaults to 1.
            timeout (int | None): Optional timeout value.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.CnRpdoRequest,
            zehnder_pb2.GatewayOperation.CnRpdoRequestType,
            {"pdid": pdid, "type": pdo_type, "zone": zone or 1, "timeout": timeout},
        )

    @log_call
    def cmd_keepalive(self) -> Awaitable[Message]:
        """Send a keepalive message.

        Returns:
            Awaitable[Message]: Awaitable resolving to the response message.
        """
        return self._send(
            zehnder_pb2.KeepAlive,
            zehnder_pb2.GatewayOperation.KeepAliveType,
            reply=False,
        )


class Message:
    """A message that is sent to the bridge.

    Attributes:
        cmd (ProtobufMessage): The command protobuf message.
        msg (ProtobufMessage): The payload protobuf message.
        src (str): The source UUID as a hex string.
        dst (str): The destination UUID as a hex string.
    """
    REQUEST_MAPPING: dict[int, type[ProtobufMessage]] = {
        zehnder_pb2.GatewayOperation.SetAddressRequestType: zehnder_pb2.SetAddressRequest,
        zehnder_pb2.GatewayOperation.RegisterAppRequestType: zehnder_pb2.RegisterAppRequest,
        zehnder_pb2.GatewayOperation.StartSessionRequestType: zehnder_pb2.StartSessionRequest,
        zehnder_pb2.GatewayOperation.CloseSessionRequestType: zehnder_pb2.CloseSessionRequest,
        zehnder_pb2.GatewayOperation.ListRegisteredAppsRequestType: zehnder_pb2.ListRegisteredAppsRequest,
        zehnder_pb2.GatewayOperation.DeregisterAppRequestType: zehnder_pb2.DeregisterAppRequest,
        zehnder_pb2.GatewayOperation.ChangePinRequestType: zehnder_pb2.ChangePinRequest,
        zehnder_pb2.GatewayOperation.GetRemoteAccessIdRequestType: zehnder_pb2.GetRemoteAccessIdRequest,
        zehnder_pb2.GatewayOperation.SetRemoteAccessIdRequestType: zehnder_pb2.SetRemoteAccessIdRequest,
        zehnder_pb2.GatewayOperation.GetSupportIdRequestType: zehnder_pb2.GetSupportIdRequest,
        zehnder_pb2.GatewayOperation.SetSupportIdRequestType: zehnder_pb2.SetSupportIdRequest,
        zehnder_pb2.GatewayOperation.GetWebIdRequestType: zehnder_pb2.GetWebIdRequest,
        zehnder_pb2.GatewayOperation.SetWebIdRequestType: zehnder_pb2.SetWebIdRequest,
        zehnder_pb2.GatewayOperation.SetPushIdRequestType: zehnder_pb2.SetPushIdRequest,
        zehnder_pb2.GatewayOperation.DebugRequestType: zehnder_pb2.DebugRequest,
        zehnder_pb2.GatewayOperation.UpgradeRequestType: zehnder_pb2.UpgradeRequest,
        zehnder_pb2.GatewayOperation.SetDeviceSettingsRequestType: zehnder_pb2.SetDeviceSettingsRequest,
        zehnder_pb2.GatewayOperation.VersionRequestType: zehnder_pb2.VersionRequest,
        zehnder_pb2.GatewayOperation.SetAddressConfirmType: zehnder_pb2.SetAddressConfirm,
        zehnder_pb2.GatewayOperation.RegisterAppConfirmType: zehnder_pb2.RegisterAppConfirm,
        zehnder_pb2.GatewayOperation.StartSessionConfirmType: zehnder_pb2.StartSessionConfirm,
        zehnder_pb2.GatewayOperation.CloseSessionConfirmType: zehnder_pb2.CloseSessionConfirm,
        zehnder_pb2.GatewayOperation.ListRegisteredAppsConfirmType: zehnder_pb2.ListRegisteredAppsConfirm,
        zehnder_pb2.GatewayOperation.DeregisterAppConfirmType: zehnder_pb2.DeregisterAppConfirm,
        zehnder_pb2.GatewayOperation.ChangePinConfirmType: zehnder_pb2.ChangePinConfirm,
        zehnder_pb2.GatewayOperation.GetRemoteAccessIdConfirmType: zehnder_pb2.GetRemoteAccessIdConfirm,
        zehnder_pb2.GatewayOperation.SetRemoteAccessIdConfirmType: zehnder_pb2.SetRemoteAccessIdConfirm,
        zehnder_pb2.GatewayOperation.GetSupportIdConfirmType: zehnder_pb2.GetSupportIdConfirm,
        zehnder_pb2.GatewayOperation.SetSupportIdConfirmType: zehnder_pb2.SetSupportIdConfirm,
        zehnder_pb2.GatewayOperation.GetWebIdConfirmType: zehnder_pb2.GetWebIdConfirm,
        zehnder_pb2.GatewayOperation.SetWebIdConfirmType: zehnder_pb2.SetWebIdConfirm,
        zehnder_pb2.GatewayOperation.SetPushIdConfirmType: zehnder_pb2.SetPushIdConfirm,
        zehnder_pb2.GatewayOperation.DebugConfirmType: zehnder_pb2.DebugConfirm,
        zehnder_pb2.GatewayOperation.UpgradeConfirmType: zehnder_pb2.UpgradeConfirm,
        zehnder_pb2.GatewayOperation.SetDeviceSettingsConfirmType: zehnder_pb2.SetDeviceSettingsConfirm,
        zehnder_pb2.GatewayOperation.VersionConfirmType: zehnder_pb2.VersionConfirm,
        zehnder_pb2.GatewayOperation.GatewayNotificationType: zehnder_pb2.GatewayNotification,
        zehnder_pb2.GatewayOperation.KeepAliveType: zehnder_pb2.KeepAlive,
        zehnder_pb2.GatewayOperation.FactoryResetType: zehnder_pb2.FactoryReset,
        zehnder_pb2.GatewayOperation.CnTimeRequestType: zehnder_pb2.CnTimeRequest,
        zehnder_pb2.GatewayOperation.CnTimeConfirmType: zehnder_pb2.CnTimeConfirm,
        zehnder_pb2.GatewayOperation.CnNodeRequestType: zehnder_pb2.CnNodeRequest,
        zehnder_pb2.GatewayOperation.CnNodeNotificationType: zehnder_pb2.CnNodeNotification,
        zehnder_pb2.GatewayOperation.CnRmiRequestType: zehnder_pb2.CnRmiRequest,
        zehnder_pb2.GatewayOperation.CnRmiResponseType: zehnder_pb2.CnRmiResponse,
        zehnder_pb2.GatewayOperation.CnRmiAsyncRequestType: zehnder_pb2.CnRmiAsyncRequest,
        zehnder_pb2.GatewayOperation.CnRmiAsyncConfirmType: zehnder_pb2.CnRmiAsyncConfirm,
        zehnder_pb2.GatewayOperation.CnRmiAsyncResponseType: zehnder_pb2.CnRmiAsyncResponse,
        zehnder_pb2.GatewayOperation.CnRpdoRequestType: zehnder_pb2.CnRpdoRequest,
        zehnder_pb2.GatewayOperation.CnRpdoConfirmType: zehnder_pb2.CnRpdoConfirm,
        zehnder_pb2.GatewayOperation.CnRpdoNotificationType: zehnder_pb2.CnRpdoNotification,
        zehnder_pb2.GatewayOperation.CnAlarmNotificationType: zehnder_pb2.CnAlarmNotification,
        zehnder_pb2.GatewayOperation.CnFupReadRegisterRequestType: zehnder_pb2.CnFupReadRegisterRequest,
        zehnder_pb2.GatewayOperation.CnFupReadRegisterConfirmType: zehnder_pb2.CnFupReadRegisterConfirm,
        zehnder_pb2.GatewayOperation.CnFupProgramBeginRequestType: zehnder_pb2.CnFupProgramBeginRequest,
        zehnder_pb2.GatewayOperation.CnFupProgramBeginConfirmType: zehnder_pb2.CnFupProgramBeginConfirm,
        zehnder_pb2.GatewayOperation.CnFupProgramRequestType: zehnder_pb2.CnFupProgramRequest,
        zehnder_pb2.GatewayOperation.CnFupProgramConfirmType: zehnder_pb2.CnFupProgramConfirm,
        zehnder_pb2.GatewayOperation.CnFupProgramEndRequestType: zehnder_pb2.CnFupProgramEndRequest,
        zehnder_pb2.GatewayOperation.CnFupProgramEndConfirmType: zehnder_pb2.CnFupProgramEndConfirm,
        zehnder_pb2.GatewayOperation.CnFupReadRequestType: zehnder_pb2.CnFupReadRequest,
        zehnder_pb2.GatewayOperation.CnFupReadConfirmType: zehnder_pb2.CnFupReadConfirm,
        zehnder_pb2.GatewayOperation.CnFupResetRequestType: zehnder_pb2.CnFupResetRequest,
        zehnder_pb2.GatewayOperation.CnFupResetConfirmType: zehnder_pb2.CnFupResetConfirm,
    }

    def __init__(self, cmd: ProtobufMessage, msg: ProtobufMessage, src: str, dst: str) -> None:
        self.cmd: ProtobufMessage = cmd
        self.msg: ProtobufMessage = msg
        self.src: str = src
        self.dst: str = dst

    def __str__(self) -> str:
        return (
            f"{self.src} -> {self.dst}: "
            f"{self.cmd.SerializeToString().hex()} {self.msg.SerializeToString().hex()}\n"
            f"{self.cmd}\n{self.msg}"
        )

    def encode(self) -> bytes:
        """Encode the message into a byte array.

        Returns:
            bytes: The encoded message.
        """
        cmd_buf = self.cmd.SerializeToString()
        msg_buf = self.msg.SerializeToString()
        cmd_len_buf = struct.pack(">H", len(cmd_buf))
        msg_len_buf = struct.pack(">L", 16 + 16 + 2 + len(cmd_buf) + len(msg_buf))
        return (
            msg_len_buf
            + bytes.fromhex(self.src)
            + bytes.fromhex(self.dst)
            + cmd_len_buf
            + cmd_buf
            + msg_buf
        )

    @classmethod
    def decode(cls, packet: bytes) -> Message:
        """Decode a packet from a byte buffer.

        Args:
            packet (bytes): The packet to decode.

        Returns:
            Message: The decoded message.
        """
        src_buf = packet[0:16]
        dst_buf = packet[16:32]
        cmd_len = struct.unpack(">H", packet[32:34])[0]
        cmd_buf = packet[34 : 34 + cmd_len]
        msg_buf = packet[34 + cmd_len :]
        cmd = zehnder_pb2.GatewayOperation()
        cmd.ParseFromString(cmd_buf)
        cmd_type = cls.REQUEST_MAPPING.get(cmd.type)
        if cmd_type is None:
            raise ValueError(f"Unknown command type: {cmd.type}")
        msg = cmd_type()
        msg.ParseFromString(msg_buf)
        return Message(cmd, msg, src_buf.hex(), dst_buf.hex())
