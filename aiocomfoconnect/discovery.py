"""
Bridge discovery utilities for aiocomfoconnect.

This module provides asynchronous UDP-based discovery of ComfoConnect LAN C bridges
on the local network or at a specified host. It defines a protocol for sending
discovery requests and parsing responses, and exposes a coroutine for performing
the discovery process.

Example:
    import asyncio
    from aiocomfoconnect.discovery import discover_bridges

    async def main():
        bridges = await discover_bridges(timeout=2)
        for bridge in bridges:
            print(f"Found bridge at {bridge.host} with UUID {bridge.uuid}")

    asyncio.run(main())

Attributes:
    DISCOVERY_REQUEST (bytes): The UDP discovery request payload.
    DEFAULT_TIMEOUT (int): Default timeout for discovery in seconds.
    BROADCAST_FALLBACK (str): Fallback broadcast address if detection fails.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import netifaces
from google.protobuf.message import DecodeError

from .bridge import Bridge
from .protobuf import zehnder_pb2

DISCOVERY_REQUEST: bytes = b"\x0a\x00"
DEFAULT_TIMEOUT: int = 1
BROADCAST_FALLBACK: str = "255.255.255.255"

_LOGGER = logging.getLogger(__name__)


class BridgeDiscoveryProtocol(asyncio.DatagramProtocol):
    """UDP Protocol for discovering ComfoConnect LAN C bridges on the local network.

    This protocol sends a UDP broadcast or unicast discovery request and listens for responses
    from available bridges. Discovered bridges are collected and returned as a list.

    Args:
        target (str | None): Specific IP address to send the discovery request to. If None, a broadcast is sent.
        timeout (int): Time in seconds to wait for responses before disconnecting.

    Attributes:
        _bridges (list[Bridge]): List of discovered Bridge instances.
        _target (str | None): Target IP address for discovery, or None for broadcast.
        _future (asyncio.Future): Future that will be set with the list of discovered bridges.
        transport (asyncio.transports.DatagramTransport | None): UDP transport for sending/receiving datagrams.
        _timeout (asyncio.Handle): Handle for the timeout callback.
    """

    def __init__(self, target: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Initialize the BridgeDiscoveryProtocol.

        Args:
            target (str | None): Target IP address for discovery, or None for broadcast.
            timeout (int): Timeout in seconds for discovery.
        """
        loop = asyncio.get_running_loop()
        self._bridges: list[Bridge] = []
        self._target: str | None = target
        self._future: asyncio.Future[list[Bridge]] = loop.create_future()
        self.transport: asyncio.transports.DatagramTransport | None = None
        self._timeout: asyncio.Handle = loop.call_later(timeout, self.disconnect)

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        """Handle connection creation and send discovery request.

        Args:
            transport (asyncio.transports.DatagramTransport): The UDP transport.
        """
        _LOGGER.debug("Socket has been created")
        self.transport = transport

        if self._target:
            _LOGGER.debug("Sending discovery request to %s:%s", self._target, Bridge.PORT)
            self.transport.sendto(DISCOVERY_REQUEST, (self._target, Bridge.PORT))
        else:
            # Determine broadcast address programmatically
            broadcast_addr = BROADCAST_FALLBACK
            try:
                gws = netifaces.gateways()
                if (default_gw := gws.get("default")) and (inet := default_gw.get(netifaces.AF_INET)):
                    default_iface = inet[1]
                    addrs = netifaces.ifaddresses(default_iface)
                    broadcast_addr = addrs[netifaces.AF_INET][0].get("broadcast", BROADCAST_FALLBACK)
            except (OSError, KeyError, ValueError, AttributeError) as e:
                _LOGGER.warning("Could not determine broadcast address, using %s: %s", BROADCAST_FALLBACK, e)
            _LOGGER.debug("Sending discovery request to broadcast:%s (%s)", Bridge.PORT, broadcast_addr)
            self.transport.sendto(DISCOVERY_REQUEST, (broadcast_addr, Bridge.PORT))

    def datagram_received(self, data: bytes | str, addr: tuple[str | Any, int]) -> None:
        """Handle received datagram and parse bridge response.

        Args:
            data (bytes | str): The received datagram data.
            addr (tuple): The address of the sender.
        """
        if data == DISCOVERY_REQUEST:
            _LOGGER.debug("Ignoring discovery request from %s:%s", addr[0], addr[1])
            return

        _LOGGER.debug("Data received from %s: %s", addr, data)
        try:
            parser = zehnder_pb2.DiscoveryOperation()  # pylint: disable=no-member
            parser.ParseFromString(data)
            self._bridges.append(Bridge(host=parser.searchGatewayResponse.ipaddress, uuid=parser.searchGatewayResponse.uuid.hex()))
        except (DecodeError, AttributeError, ValueError) as exc:
            _LOGGER.error("Failed to parse discovery response from %s: %s", addr, exc)
            return

        # If a target is specified, stop after first response
        if self._target:
            self._timeout.cancel()
            self.disconnect()

    def disconnect(self) -> None:
        """Disconnect the socket and resolve the discovery future."""
        if self.transport:
            self.transport.close()
        if not self._future.done():
            self._future.set_result(self._bridges)

    def get_bridges(self) -> asyncio.Future[list[Bridge]]:
        """Return the discovered bridges future.

        Returns:
            asyncio.Future[list[Bridge]]: Future that resolves to a list of Bridge objects.
        """
        return self._future


async def discover_bridges(host: str | None = None, timeout: int = DEFAULT_TIMEOUT, loop: asyncio.AbstractEventLoop | None = None) -> list[Bridge]:
    """Discover ComfoConnect bridges on the local network or at a specified host.

    Send a UDP broadcast (or unicast if a host is specified) to discover available
    ComfoConnect bridges. Return a list of discovered Bridge instances.

    Args:
        host (str | None): The IP address of a specific bridge to discover. If None,
            a broadcast is sent to discover all available bridges.
        timeout (int): The time in seconds to wait for responses.
        loop (asyncio.AbstractEventLoop | None): The event loop to use. If None,
            the running event loop is used.

    Returns:
        list[Bridge]: A list of discovered Bridge objects.

    Raises:
        Exception: Any exceptions raised by the underlying asyncio transport or protocol.

    Example:
        bridges = await discover_bridges(timeout=2)
    """
    if loop is None:
        loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: BridgeDiscoveryProtocol(host, timeout),
        local_addr=("0.0.0.0", 0),
        allow_broadcast=not host,
    )

    try:
        return await protocol.get_bridges()
    finally:
        transport.close()
